# Purpose: Authentication endpoints for Telegram WebApp.
# Context: Simple auth based on Telegram ID, validate initData.
# Requirements: /auth/me endpoint, role detection (parent/child).

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_session
from app.db.models import Parent, Child
from app.api.schemas import UserInfo
from app.core import get_logger

router = APIRouter(prefix="/auth", tags=["auth"])
logger = get_logger(__name__)


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    x_tg_user_id: int = Header(alias="X-TG-User-ID")
) -> UserInfo:
    """
    Получить информацию о текущем пользователе по Telegram ID.
    
    В MVP используем простую аутентификацию по заголовку X-TG-User-ID.
    В продакшене нужно валидировать initData от Telegram WebApp.
    """
    if not x_tg_user_id:
        raise HTTPException(status_code=401, detail="Missing Telegram user ID")
    
    # Проверяем, есть ли родитель с таким tg_id
    parent_result = await session.execute(
        select(Parent).where(Parent.tg_id == x_tg_user_id, Parent.is_active == True)
    )
    parent = parent_result.scalar_one_or_none()
    
    if parent:
        return UserInfo(
            role="parent",
            user_id=parent.id,
            tg_id=x_tg_user_id,
            family_id=parent.family_id
        )
    
    # Проверяем, есть ли ребёнок с таким tg_id (если добавим поле tg_id к Child)
    # Пока что ребёнок не имеет собственного tg_id в нашей модели
    
    # Если пользователь не найден, создаём нового родителя
    # Сначала нужно создать семью
    from app.db.models import Family
    
    family = Family()
    session.add(family)
    await session.flush()
    
    new_parent = Parent(
        tg_id=x_tg_user_id,
        family_id=family.id,
        is_active=True
    )
    session.add(new_parent)
    await session.commit()
    await session.refresh(new_parent)
    
    logger.info(f"Created new parent with tg_id={x_tg_user_id}, family_id={family.id}")
    
    return UserInfo(
        role="parent",
        user_id=new_parent.id,
        tg_id=x_tg_user_id,
        family_id=new_parent.family_id
    )


@router.get("/me", response_model=UserInfo)
async def get_me(
    current_user: UserInfo = Depends(get_current_user)
) -> UserInfo:
    """Получить информацию о текущем пользователе."""
    return current_user