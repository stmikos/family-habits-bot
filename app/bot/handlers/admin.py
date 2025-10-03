# Purpose: Admin handlers for debugging and management.
# Context: Команды для администрирования бота.
# Requirements: /info, /stats для отладки.

from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.models import Parent, Child, Task, Family
from app.core.config import settings
from app.core import get_logger

router = Router()
logger = get_logger(__name__)


@router.message(Command("info"))
async def info_handler(message: types.Message, session: AsyncSession):
    """Информация о пользователе."""
    user_id = message.from_user.id
    
    # Проверяем родителя
    result = await session.execute(
        select(Parent).where(Parent.tg_id == user_id)
    )
    parent = result.scalar_one_or_none()
    
    # Проверяем ребёнка
    result = await session.execute(
        select(Child).where(Child.tg_id == user_id)
    )
    child = result.scalar_one_or_none()
    
    if parent:
        # Статистика семьи
        children_count = await session.scalar(
            select(func.count(Child.id)).where(Child.family_id == parent.family_id)
        )
        tasks_count = await session.scalar(
            select(func.count(Task.id)).where(Task.parent_id == parent.id)
        )
        
        await message.answer(
            f"ℹ️ <b>Информация о пользователе</b>\n\n"
            f"🆔 Telegram ID: <code>{user_id}</code>\n"
            f"👤 Роль: <b>Родитель</b>\n"
            f"🏠 ID семьи: <code>{parent.family_id}</code>\n"
            f"👨‍👩‍👧‍👦 Детей: <b>{children_count}</b>\n"
            f"📝 Создано заданий: <b>{tasks_count}</b>"
        )
    elif child:
        # Статистика ребёнка
        tasks_count = await session.scalar(
            select(func.count(Task.id)).where(Task.child_id == child.id)
        )
        
        await message.answer(
            f"ℹ️ <b>Информация о пользователе</b>\n\n"
            f"🆔 Telegram ID: <code>{user_id}</code>\n"
            f"👤 Роль: <b>Ребёнок</b>\n"
            f"👦👧 Имя: <b>{child.name}</b>\n"
            f"🏠 ID семьи: <code>{child.family_id}</code>\n"
            f"⭐ Очки: <b>{child.points}</b>\n"
            f"🪙 Монеты: <b>{child.coins}</b>\n"
            f"📝 Заданий получено: <b>{tasks_count}</b>"
        )
    else:
        await message.answer(
            f"ℹ️ <b>Информация о пользователе</b>\n\n"
            f"🆔 Telegram ID: <code>{user_id}</code>\n"
            f"👤 Роль: <b>Не зарегистрирован</b>\n\n"
            f"📱 Напишите /start для регистрации"
        )


@router.message(Command("stats"))
async def stats_handler(message: types.Message, session: AsyncSession):
    """Общая статистика бота."""
    # Только для админов
    if message.from_user.id not in settings.ADMIN_USER_IDS:
        return
    
    families_count = await session.scalar(select(func.count(Family.id)))
    parents_count = await session.scalar(select(func.count(Parent.id)))
    children_count = await session.scalar(select(func.count(Child.id)))
    tasks_count = await session.scalar(select(func.count(Task.id)))
    
    await message.answer(
        f"📊 <b>Статистика Family Habit Bot</b>\n\n"
        f"🏠 Семей: <b>{families_count}</b>\n"
        f"👨‍👩‍👧‍👦 Родителей: <b>{parents_count}</b>\n"
        f"👦👧 Детей: <b>{children_count}</b>\n"
        f"📝 Заданий создано: <b>{tasks_count}</b>"
    )