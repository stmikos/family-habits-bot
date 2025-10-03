# Purpose: Task service layer for Family Habit Bot.
# Context: Business logic для работы с заданиями.
# Requirements: Создание, получение, обновление заданий.

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.db.models import Task, Child, TaskStatus, CheckIn, PointsLedger
from app.core import get_logger

logger = get_logger(__name__)


class TaskService:
    """Сервис для работы с заданиями."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_tasks_for_child(self, child_id: int, status: Optional[TaskStatus] = None) -> List[Task]:
        """Получить задания для ребёнка."""
        query = select(Task).where(Task.child_id == child_id)
        
        if status:
            query = query.where(Task.status == status)
        
        query = query.order_by(Task.created_at.desc())
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_tasks_by_parent(self, parent_id: int) -> List[Task]:
        """Получить все задания, созданные родителем."""
        result = await self.session.execute(
            select(Task).where(Task.parent_id == parent_id)
            .order_by(Task.created_at.desc())
        )
        return list(result.scalars().all())

    async def submit_task(self, task_id: int, child_id: int, note: Optional[str] = None, media_id: Optional[str] = None) -> bool:
        """Сдать задание на проверку."""
        # Проверяем, что задание принадлежит ребёнку
        task = await self.session.get(Task, task_id)
        if not task or task.child_id != child_id:
            return False

        # Проверяем статус
        if task.status != TaskStatus.new:
            return False

        # Создаём чекин
        checkin = CheckIn(
            task_id=task_id,
            child_id=child_id,
            note=note,
            media_id=media_id
        )
        self.session.add(checkin)

        # Обновляем статус задания
        task.status = TaskStatus.done
        await self.session.commit()

        logger.info(f"Task {task_id} submitted by child {child_id}")
        return True

    async def approve_task(self, task_id: int, parent_id: int) -> bool:
        """Одобрить выполненное задание."""
        task = await self.session.get(Task, task_id)
        if not task or task.parent_id != parent_id:
            return False

        if task.status != TaskStatus.done:
            return False

        # Обновляем статус
        task.status = TaskStatus.approved
        
        # Начисляем очки и монеты ребёнку
        child = await self.session.get(Child, task.child_id)
        if child:
            child.points += task.points
            child.coins += task.coins

            # Записываем в журнал
            ledger_entry = PointsLedger(
                child_id=child.id,
                delta_points=task.points,
                delta_coins=task.coins,
                reason=f"Выполнено задание: {task.title}",
                ref_id=task.id
            )
            self.session.add(ledger_entry)

        await self.session.commit()
        logger.info(f"Task {task_id} approved, child {child.id} got {task.points} points and {task.coins} coins")
        return True

    async def reject_task(self, task_id: int, parent_id: int) -> bool:
        """Отклонить выполненное задание."""
        task = await self.session.get(Task, task_id)
        if not task or task.parent_id != parent_id:
            return False

        if task.status != TaskStatus.done:
            return False

        # Обновляем статус
        task.status = TaskStatus.rejected
        await self.session.commit()

        logger.info(f"Task {task_id} rejected by parent {parent_id}")
        return True

    async def get_pending_tasks(self, parent_id: int) -> List[Task]:
        """Получить задания, ожидающие проверки."""
        result = await self.session.execute(
            select(Task).where(
                and_(
                    Task.parent_id == parent_id,
                    Task.status == TaskStatus.done
                )
            ).order_by(Task.updated_at.desc())
        )
        return list(result.scalars().all())

    async def get_task_with_checkin(self, task_id: int) -> Optional[tuple[Task, Optional[CheckIn]]]:
        """Получить задание с последним чекином."""
        task = await self.session.get(Task, task_id)
        if not task:
            return None

        # Получаем последний чекин
        result = await self.session.execute(
            select(CheckIn).where(CheckIn.task_id == task_id)
            .order_by(CheckIn.created_at.desc())
            .limit(1)
        )
        checkin = result.scalar_one_or_none()

        return task, checkin