# Purpose: Хендлеры для детей - выполнение задач, просмотр очков.
# Context: Child-specific bot functionality, task submission, balance checking.
# Requirements: Task list, submission interface, points display.

from aiogram import Router, types
from aiogram.filters import Command

from app.core import get_logger

logger = get_logger(__name__)
router = Router()


@router.message(Command("child"))
async def child_menu(message: types.Message):
    """
    Главное меню для детей.
    
    TODO: Реализовать после создания роутов API.
    """
    user = message.from_user
    logger.info(f"Child menu requested by user {user.id}")
    
    menu_text = (
        "👶 <b>Меню ребёнка</b>\n\n"
        "В веб-приложении доступны:\n"
        "• 📋 Мои задания\n"
        "• 📤 Сдача выполненных задач\n"
        "• 🪙 Мой баланс очков и монет\n"
        "• 🛒 Магазин наград\n"
        "• 🏆 Мои достижения\n\n"
        "Откройте веб-приложение для выполнения заданий!"
    )
    
    await message.answer(text=menu_text)