# Purpose: Task management endpoints.
# Context: CRUD operations for tasks, including approval workflow.
# Requirements: /tasks endpoints, access control by parent/child role.

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional

from app.db.session import get_session
from app.db.models import Task, TaskStatus, TaskType
from app.api.schemas import UserInfo, Task as TaskSchema, TaskCreate, TaskUpdate
from app.api.routes.auth import get_current_user
from app.services.task_service import TaskService
from app.core import get_logger

router = APIRouter(prefix="/tasks", tags=["tasks"])
logger = get_logger(__name__)


@router.get("", response_model=List[TaskSchema])
async def list_tasks(
    child_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session),
    current_user: UserInfo = Depends(get_current_user)
) -> List[TaskSchema]:
    """Получить список задач с фильтрацией."""
    
    # Базовый запрос
    query = select(Task)
    conditions = []
    
    if current_user.role == "parent":
        # Родитель видит задачи своих детей
        conditions.append(Task.parent_id == current_user.user_id)
    else:
        # Ребёнок видит только свои задачи
        conditions.append(Task.child_id == current_user.user_id)
    
    # Фильтр по ребёнку (только для родителя)
    if child_id and current_user.role == "parent":
        conditions.append(Task.child_id == child_id)
    
    # Фильтр по статусу
    if status:
        try:
            task_status = TaskStatus(status)
            conditions.append(Task.status == task_status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(Task.created_at.desc())
    
    result = await session.execute(query)
    tasks = result.scalars().all()
    
    return [TaskSchema.model_validate(task) for task in tasks]


@router.post("", response_model=TaskSchema)
async def create_task(
    data: TaskCreate,
    session: AsyncSession = Depends(get_session),
    current_user: UserInfo = Depends(get_current_user)
) -> TaskSchema:
    """Создать новое задание."""
    if current_user.role != "parent":
        raise HTTPException(status_code=403, detail="Only parents can create tasks")
    
    # Создаём задачу с parent_id из текущего пользователя
    task = Task(
        title=data.title,
        description=data.description,
        type=data.type,
        points=data.points,
        coins=data.coins,
        due_at=data.due_at,
        child_id=data.child_id,
        parent_id=current_user.user_id
    )
    
    session.add(task)
    await session.commit()
    await session.refresh(task)
    
    logger.info(f"Created task: {task.title} for child {task.child_id}")
    
    return TaskSchema.model_validate(task)


@router.get("/{task_id}", response_model=TaskSchema)
async def get_task(
    task_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: UserInfo = Depends(get_current_user)
) -> TaskSchema:
    """Получить информацию о задаче."""
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Проверяем доступ
    if current_user.role == "parent" and task.parent_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role == "child" and task.child_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return TaskSchema.model_validate(task)


@router.put("/{task_id}", response_model=TaskSchema)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: UserInfo = Depends(get_current_user)
) -> TaskSchema:
    """Обновить задание."""
    if current_user.role != "parent":
        raise HTTPException(status_code=403, detail="Only parents can update tasks")
    
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.parent_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Обновляем поля
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    await session.commit()
    await session.refresh(task)
    
    logger.info(f"Updated task {task_id}: {update_data}")
    
    return TaskSchema.model_validate(task)


@router.post("/{task_id}/approve", response_model=TaskSchema)
async def approve_task(
    task_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: UserInfo = Depends(get_current_user)
) -> TaskSchema:
    """Одобрить задание."""
    if current_user.role != "parent":
        raise HTTPException(status_code=403, detail="Only parents can approve tasks")
    
    task_service = TaskService(session)
    task = await task_service.approve_task(task_id, current_user.user_id)
    
    return task


@router.post("/{task_id}/reject", response_model=TaskSchema)
async def reject_task(
    task_id: int,
    reason: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    current_user: UserInfo = Depends(get_current_user)
) -> TaskSchema:
    """Отклонить задание."""
    if current_user.role != "parent":
        raise HTTPException(status_code=403, detail="Only parents can reject tasks")
    
    task_service = TaskService(session)
    task = await task_service.reject_task(task_id, current_user.user_id, reason)
    
    return task