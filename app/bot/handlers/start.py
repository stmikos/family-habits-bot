# Purpose: Хендлер команды /start и выбора роли пользователя.
# Context: Initial bot interaction, user registration, role assignment.
# Requirements: Register parent/child, show main menu, handle WebApp launch.

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from app.core import get_logger, settings

logger = get_logger(__name__)
router = Router()


@router.message(Command("start"))
async def start_command(message: types.Message):
    """
    Обработчик команды /start.
    
    Показывает главное меню с кнопкой запуска MiniApp.
    """
    user = message.from_user
    logger.info(f"User {user.id} ({user.full_name}) started bot")
    
    # Кнопка для запуска WebApp
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Открыть Family Habit",
                    web_app=WebAppInfo(url=settings.webapp_url)
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ О проекте",
                    callback_data="about"
                )
            ]
        ]
    )
    
    welcome_text = (
        f"👋 Привет, <b>{user.full_name}</b>!\n\n"
        "Добро пожаловать в <b>Family Habit</b> — приложение для семейного трекинга привычек.\n\n"
        "🎯 <b>Для родителей:</b> создавайте задания, отслеживайте прогресс, награждайте детей\n"
        "👶 <b>Для детей:</b> выполняйте задания, зарабатывайте очки, покупайте награды\n\n"
        "Нажмите кнопку ниже, чтобы открыть приложение:"
    )
    
    await message.answer(
        text=welcome_text,
        reply_markup=keyboard
    )


@router.callback_query(lambda c: c.data == "about")
async def about_callback(callback_query: types.CallbackQuery):
    """Информация о проекте."""
    about_text = (
        "📱 <b>Family Habit</b>\n\n"
        "Помогаем семьям формировать полезные привычки через игровую механику:\n\n"
        "✅ Создание заданий с дедлайнами\n"
        "📸 Отчёты с фото и видео\n"
        "🏆 Система очков и наград\n"
        "🛒 Внутренний магазин призов\n"
        "📊 Статистика прогресса\n\n"
        "Версия: 1.0.0 MVP"
    )
    
    await callback_query.answer()
    await callback_query.message.edit_text(
        text=about_text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔙 Назад",
                        callback_data="back_to_main"
                    )
                ]
            ]
        )
    )


@router.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main_callback(callback_query: types.CallbackQuery):
    """Возврат к главному меню."""
    await callback_query.answer()
    
    # Повторяем логику start_command
    user = callback_query.from_user
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Открыть Family Habit",
                    web_app=WebAppInfo(url=settings.webapp_url)
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ О проекте",
                    callback_data="about"
                )
            ]
        ]
    )
    
    welcome_text = (
        f"👋 Привет, <b>{user.full_name}</b>!\n\n"
        "Добро пожаловать в <b>Family Habit</b> — приложение для семейного трекинга привычек.\n\n"
        "🎯 <b>Для родителей:</b> создавайте задания, отслеживайте прогресс, награждайте детей\n"
        "👶 <b>Для детей:</b> выполняйте задания, зарабатывайте очки, покупайте награды\n\n"
        "Нажмите кнопку ниже, чтобы открыть приложение:"
    )
    
    await callback_query.message.edit_text(
        text=welcome_text,
        reply_markup=keyboard
    )