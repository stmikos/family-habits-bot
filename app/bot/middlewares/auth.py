# Purpose: Database and Auth middlewares for bot.
# Context: Inject database session and user authentication.
# Requirements: AsyncSession для handlers, определение роли пользователя.

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import SessionLocal
from app.db.models import Parent, Child
from app.core import get_logger

logger = get_logger(__name__)


class DatabaseMiddleware(BaseMiddleware):
    """Middleware для внедрения database session в handlers."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        async with SessionLocal() as session:
            data["session"] = session
            return await handler(event, data)


class AuthMiddleware(BaseMiddleware):
    """Middleware для определения роли пользователя."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Получаем user_id из события
        user_id = None
        if hasattr(event, 'from_user') and event.from_user:
            user_id = event.from_user.id
        
        if user_id:
            session: AsyncSession = data.get("session")
            if session:
                # Определяем роль пользователя
                from sqlalchemy import select
                
                # Проверяем родителя
                result = await session.execute(
                    select(Parent).where(Parent.tg_id == user_id)
                )
                parent = result.scalar_one_or_none()
                
                if parent:
                    data["user_role"] = "parent"
                    data["user_db_id"] = parent.id
                    data["family_id"] = parent.family_id
                else:
                    # Проверяем ребёнка
                    result = await session.execute(
                        select(Child).where(Child.tg_id == user_id)
                    )
                    child = result.scalar_one_or_none()
                    
                    if child:
                        data["user_role"] = "child"
                        data["user_db_id"] = child.id
                        data["family_id"] = child.family_id
                    else:
                        data["user_role"] = "unknown"
        
        return await handler(event, data)