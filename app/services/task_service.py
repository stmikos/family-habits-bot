# Purpose: Реализовать сервис TaskService с методами create, submit, approve, reject.
# Context: см. модели в app/db/models.py и схемы в app/api/schemas.py.
# Requirements:
# - методы атомарные, используют сессию SQLAlchemy через зависимость get_session
# - submit(task_id, child_id, payload) валидирует тип и сохраняет media/text
# - approve(task_id, parent_id) меняет статус и начисляет очки
# - reject(task_id, parent_id, reason) меняет статус, создаёт запись об отказе
# - логировать и возвращать pydantic DTO

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.core import get_logger, TaskNotFoundError, ChildNotFoundError, ParentNotFoundError, TaskAlreadySubmittedError, DomainError
from app.db.models import Task, Child, Parent, CheckIn, PointsLedger, TaskStatus, TaskType
from app.api.schemas import TaskCreate, TaskUpdate, Task as TaskSchema, CheckInCreate


logger = get_logger(__name__)


class TaskService:
    """Сервис для работы с заданиями."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_task(self, data: TaskCreate) -> TaskSchema:
        """
        Создать задание для ребёнка.
        
        Args:
            data: Данные для создания задания.
            
        Returns:
            TaskSchema: Созданное задание.
            
        Raises:
            ChildNotFoundError: Если ребёнок не найден.
            ParentNotFoundError: Если родитель не найден.
        """
        # Проверяем существование ребёнка
        child = await self.session.get(Child, data.child_id)
        if not child or not child.is_active:
            raise ChildNotFoundError(data.child_id)
        
        # Проверяем существование родителя
        parent = await self.session.get(Parent, data.parent_id)
        if not parent or not parent.is_active:
            raise ParentNotFoundError(data.parent_id)
        
        # Проверяем, что ребёнок принадлежит семье родителя
        if child.family_id != parent.family_id:
            raise DomainError(
                code="family_mismatch",
                message="Ребёнок не принадлежит семье родителя"
            )
        
        # TODO: Проверить лимиты тарифного плана
        
        # Создаём задание
        task = Task(
            parent_id=data.parent_id,
            child_id=data.child_id,
            title=data.title,
            description=data.description,
            type=TaskType(data.type),
            points=data.points,
            coins=data.coins,
            due_at=data.due_at,
            status=TaskStatus.new
        )
        
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        
        logger.info(f"Task created: {task.id} for child {data.child_id} by parent {data.parent_id}")
        
        return TaskSchema.model_validate(task)
    
    async def get_tasks(
        self, 
        child_id: Optional[int] = None,
        parent_id: Optional[int] = None,
        status: Optional[TaskStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[TaskSchema]:
        """
        Получить список заданий с фильтрацией.
        
        Args:
            child_id: ID ребёнка для фильтрации.
            parent_id: ID родителя для фильтрации.
            status: Статус заданий для фильтрации.
            limit: Максимальное количество результатов.
            offset: Смещение для пагинации.
            
        Returns:
            List[TaskSchema]: Список заданий.
        """
        query = select(Task).where(Task.status != TaskStatus.new)  # Базовый фильтр
        
        if child_id:
            query = query.where(Task.child_id == child_id)
        if parent_id:
            query = query.where(Task.parent_id == parent_id)
        if status:
            query = query.where(Task.status == status)
        
        query = query.order_by(Task.created_at.desc()).limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        tasks = result.scalars().all()
        
        return [TaskSchema.model_validate(task) for task in tasks]
    
    async def get_task(self, task_id: int) -> TaskSchema:
        """
        Получить задание по ID.
        
        Args:
            task_id: ID задания.
            
        Returns:
            TaskSchema: Задание.
            
        Raises:
            TaskNotFoundError: Если задание не найдено.
        """
        task = await self.session.get(Task, task_id)
        if not task:
            raise TaskNotFoundError(task_id)
        
        return TaskSchema.model_validate(task)
    
    async def submit_task(self, task_id: int, child_id: int, checkin_data: CheckInCreate) -> TaskSchema:
        """
        Сдать задание (создать check-in).
        
        Args:
            task_id: ID задания.
            child_id: ID ребёнка.
            checkin_data: Данные check-in.
            
        Returns:
            TaskSchema: Обновлённое задание.
            
        Raises:
            TaskNotFoundError: Если задание не найдено.
            TaskAlreadySubmittedError: Если задание уже сдано.
            DomainError: Если ребёнок не может сдать это задание.
        """
        task = await self.session.get(Task, task_id)
        if not task:
            raise TaskNotFoundError(task_id)
        
        if task.child_id != child_id:
            raise DomainError(
                code="access_denied",
                message="Ребёнок не может сдать чужое задание"
            )
        
        if task.status in [TaskStatus.done, TaskStatus.approved, TaskStatus.rejected]:
            raise TaskAlreadySubmittedError(task_id)
        
        # Валидация типа задания
        if task.type == TaskType.text and not checkin_data.note:
            raise DomainError(
                code="validation_error",
                message="Для текстового задания требуется заметка"
            )
        elif task.type in [TaskType.photo, TaskType.video] and not checkin_data.media_id:
            raise DomainError(
                code="validation_error",
                message="Для фото/видео задания требуется медиафайл"
            )
        
        # Создаём check-in
        checkin = CheckIn(
            task_id=task_id,
            child_id=child_id,
            note=checkin_data.note,
            media_id=checkin_data.media_id
        )
        
        # Обновляем статус задания
        task.status = TaskStatus.done
        task.updated_at = datetime.utcnow()
        
        self.session.add(checkin)
        await self.session.commit()
        await self.session.refresh(task)
        
        logger.info(f"Task {task_id} submitted by child {child_id}")
        
        return TaskSchema.model_validate(task)
    
    async def approve_task(self, task_id: int, parent_id: int) -> TaskSchema:
        """
        Одобрить задание и начислить очки.
        
        Args:
            task_id: ID задания.
            parent_id: ID родителя.
            
        Returns:
            TaskSchema: Обновлённое задание.
            
        Raises:
            TaskNotFoundError: Если задание не найдено.
            DomainError: Если родитель не может одобрить это задание.
        """
        task = await self.session.get(Task, task_id)
        if not task:
            raise TaskNotFoundError(task_id)
        
        if task.parent_id != parent_id:
            raise DomainError(
                code="access_denied",
                message="Родитель не может одобрить чужое задание"
            )
        
        if task.status != TaskStatus.done:
            raise DomainError(
                code="invalid_status",
                message="Можно одобрить только выполненное задание"
            )
        
        # Идемпотентность - если уже одобрено, ничего не делаем
        if task.status == TaskStatus.approved:
            logger.info(f"Task {task_id} already approved")
            return TaskSchema.model_validate(task)
        
        # Получаем ребёнка для начисления очков
        child = await self.session.get(Child, task.child_id)
        if not child:
            raise ChildNotFoundError(task.child_id)
        
        # Начисляем очки и монеты
        child.points += task.points
        child.coins += task.coins
        
        # Записываем в ledger
        ledger_entry = PointsLedger(
            child_id=task.child_id,
            delta_points=task.points,
            delta_coins=task.coins,
            reason="task_approved",
            ref_id=task_id
        )
        
        # Обновляем статус задания
        task.status = TaskStatus.approved
        task.updated_at = datetime.utcnow()
        
        self.session.add(ledger_entry)
        await self.session.commit()
        await self.session.refresh(task)
        
        logger.info(f"Task {task_id} approved: +{task.points} points, +{task.coins} coins for child {task.child_id}")
        
        return TaskSchema.model_validate(task)
    
    async def reject_task(self, task_id: int, parent_id: int, reason: Optional[str] = None) -> TaskSchema:
        """
        Отклонить задание.
        
        Args:
            task_id: ID задания.
            parent_id: ID родителя.
            reason: Причина отклонения.
            
        Returns:
            TaskSchema: Обновлённое задание.
            
        Raises:
            TaskNotFoundError: Если задание не найдено.
            DomainError: Если родитель не может отклонить это задание.
        """
        task = await self.session.get(Task, task_id)
        if not task:
            raise TaskNotFoundError(task_id)
        
        if task.parent_id != parent_id:
            raise DomainError(
                code="access_denied",
                message="Родитель не может отклонить чужое задание"
            )
        
        if task.status not in [TaskStatus.done, TaskStatus.in_progress]:
            raise DomainError(
                code="invalid_status",
                message="Можно отклонить только выполненное или активное задание"
            )
        
        # Обновляем статус задания
        task.status = TaskStatus.rejected
        task.updated_at = datetime.utcnow()
        
        # TODO: Сохранить причину отклонения в отдельную таблицу
        
        await self.session.commit()
        await self.session.refresh(task)
        
        logger.info(f"Task {task_id} rejected by parent {parent_id}: {reason}")
        
        return TaskSchema.model_validate(task)