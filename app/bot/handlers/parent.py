# Purpose: Хендлеры для родителей - создание и модерация задач.
# Context: Parent-specific bot functionality, task management, notifications.
# Requirements: Task creation, approval/rejection, family management.

from aiogram import Router, types
from aiogram.filters import Command

from app.core import get_logger

logger = get_logger(__name__)
router = Router()


@router.message(Command("parent"))
async def parent_menu(message: types.Message):
    """
    Главное меню для родителей.
    
    TODO: Реализовать после создания роутов API.
    """
    user = message.from_user
    logger.info(f"Parent menu requested by user {user.id}")
    
    menu_text = (
        "👨‍👩‍👧‍👦 <b>Меню родителя</b>\n\n"
        "В веб-приложении доступны:\n"
        "• 📝 Создание заданий\n"
        "• 👀 Просмотр выполненных задач\n"
        "• ✅ Одобрение/отклонение\n"
        "• 👶 Управление детьми\n"
        "• 📊 Статистика семьи\n\n"
        "Откройте веб-приложение для полного функционала!"
    )
    
    await message.answer(text=menu_text)