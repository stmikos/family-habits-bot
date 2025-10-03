# Purpose: Children management endpoints.
# Context: CRUD operations for children in family.
# Requirements: /children endpoints, parent access control.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.session import get_session
from app.db.models import Child
from app.api.schemas import UserInfo, Child as ChildSchema, ChildCreate, ChildUpdate
from app.api.routes.auth import get_current_user
from app.core import get_logger

router = APIRouter(prefix="/children", tags=["children"])
logger = get_logger(__name__)


@router.get("", response_model=List[ChildSchema])
async def list_children(
    session: AsyncSession = Depends(get_session),
    current_user: UserInfo = Depends(get_current_user)
) -> List[ChildSchema]:
    """Получить список детей в семье."""
    if current_user.role != "parent":
        raise HTTPException(status_code=403, detail="Only parents can list children")
    
    result = await session.execute(
        select(Child).where(Child.family_id == current_user.family_id)
    )
    children = result.scalars().all()
    
    return [ChildSchema.model_validate(child) for child in children]


@router.post("", response_model=ChildSchema)
async def create_child(
    data: ChildCreate,
    session: AsyncSession = Depends(get_session),
    current_user: UserInfo = Depends(get_current_user)
) -> ChildSchema:
    """Создать нового ребёнка в семье."""
    if current_user.role != "parent":
        raise HTTPException(status_code=403, detail="Only parents can create children")
    
    child = Child(
        family_id=current_user.family_id,
        name=data.name,
        points=0,
        coins=0
    )
    
    session.add(child)
    await session.commit()
    await session.refresh(child)
    
    logger.info(f"Created child: {child.name} for family {current_user.family_id}")
    
    return ChildSchema.model_validate(child)


@router.get("/{child_id}", response_model=ChildSchema)
async def get_child(
    child_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: UserInfo = Depends(get_current_user)
) -> ChildSchema:
    """Получить информацию о ребёнке."""
    child = await session.get(Child, child_id)
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    
    # Проверяем доступ
    if child.family_id != current_user.family_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return ChildSchema.model_validate(child)


@router.put("/{child_id}", response_model=ChildSchema)
async def update_child(
    child_id: int,
    data: ChildUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: UserInfo = Depends(get_current_user)
) -> ChildSchema:
    """Обновить информацию о ребёнке."""
    if current_user.role != "parent":
        raise HTTPException(status_code=403, detail="Only parents can update children")
    
    child = await session.get(Child, child_id)
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    
    if child.family_id != current_user.family_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Обновляем только переданные поля
    if data.name is not None:
        child.name = data.name
    
    await session.commit()
    await session.refresh(child)
    
    logger.info(f"Updated child {child_id}: {data.model_dump(exclude_unset=True)}")
    
    return ChildSchema.model_validate(child)