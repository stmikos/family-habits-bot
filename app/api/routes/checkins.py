# Purpose: Check-ins endpoints for task submission.
# Context: Children submit tasks, parents see submissions.
# Requirements: /checkins endpoint, child access for submit.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.session import get_session
from app.db.models import CheckIn, Task, TaskStatus
from app.api.schemas import UserInfo, CheckIn as CheckInSchema, CheckInCreate
from app.api.routes.auth import get_current_user
from app.services.task_service import TaskService
from app.core import get_logger

router = APIRouter(prefix="/checkins", tags=["checkins"])
logger = get_logger(__name__)


@router.post("", response_model=CheckInSchema)
async def submit_checkin(
    data: CheckInCreate,
    session: AsyncSession = Depends(get_session),
    current_user: UserInfo = Depends(get_current_user)
) -> CheckInSchema:
    """Сдать задание (создать check-in)."""
    # Проверяем, что пользователь может сдавать это задание
    task = await session.get(Task, data.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Если это ребёнок, проверяем, что он сдаёт своё задание
    if current_user.role == "child" and task.child_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You can only submit your own tasks")
    
    # Если это родитель, проверяем, что он сдаёт задание своих детей
    if current_user.role == "parent" and task.parent_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You can only submit tasks for your children")
    
    # child_id берём из задачи (task.child_id)
    child_id = task.child_id
    
    # Создаём check-in напрямую
    checkin = CheckIn(
        task_id=data.task_id,
        child_id=child_id,
        note=data.note,
        media_id=data.media_id
    )
    
    session.add(checkin)
    
    # Меняем статус задачи на "done"
    task.status = TaskStatus.done
    
    await session.commit()
    await session.refresh(checkin)
    
    logger.info(f"Created check-in for task {data.task_id} by child {child_id}")
    
    return CheckInSchema.model_validate(checkin)


@router.get("", response_model=List[CheckInSchema])
async def list_checkins(
    task_id: int = None,
    session: AsyncSession = Depends(get_session),
    current_user: UserInfo = Depends(get_current_user)
) -> List[CheckInSchema]:
    """Получить список check-ins."""
    query = select(CheckIn)
    
    if task_id:
        # Проверяем доступ к задаче
        task = await session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if current_user.role == "parent" and task.parent_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        elif current_user.role == "child" and task.child_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        query = query.where(CheckIn.task_id == task_id)
    else:
        # Показываем check-ins для задач, к которым есть доступ
        if current_user.role == "child":
            query = query.where(CheckIn.child_id == current_user.user_id)
        else:
            # Для родителя нужно джойнить с Task
            query = query.join(Task).where(Task.parent_id == current_user.user_id)
    
    query = query.order_by(CheckIn.created_at.desc())
    
    result = await session.execute(query)
    checkins = result.scalars().all()
    
    return [CheckInSchema.model_validate(checkin) for checkin in checkins]