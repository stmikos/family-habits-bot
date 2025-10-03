# Purpose: Хендлеры для детей - выполнение задач, просмотр очков.
# Context: Child-specific bot functionality, task submission, balance checking.
# Requirements: Task list, submission interface, points display.

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.core import get_logger

logger = get_logger(__name__)
router = Router()


@router.message(Command("child"))
async def child_menu(message: types.Message):
    """
    Главное меню для детей.
    """
    user = message.from_user
    logger.info(f"Child menu requested by user {user.id}")
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📋 Мои задания",
                    callback_data="child_tasks"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🪙 Баланс",
                    callback_data="child_balance"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🛒 Магазин",
                    callback_data="child_shop"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎒 Мои покупки",
                    callback_data="child_inventory"
                )
            ]
        ]
    )
    
    menu_text = (
        "👶 <b>Меню ребёнка</b>\n\n"
        "Выберите действие:"
    )
    
    await message.answer(text=menu_text, reply_markup=keyboard)


@router.callback_query(F.data == "child_shop")
async def show_shop(callback_query: types.CallbackQuery):
    """
    Показать магазин товаров.
    
    TODO: Интеграция с API для получения списка товаров.
    Пока показываем заглушку.
    """
    await callback_query.answer()
    
    shop_text = (
        "🛒 <b>Магазин наград</b>\n\n"
        "Здесь можно купить награды за монеты!\n\n"
        "Товары будут доступны через веб-приложение.\n"
        "Нажмите кнопку ниже, чтобы открыть магазин:"
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Открыть магазин",
                    url="https://t.me/your_bot_name/shop"  # TODO: заменить на реальный URL
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="back_to_child_menu"
                )
            ]
        ]
    )
    
    await callback_query.message.edit_text(
        text=shop_text,
        reply_markup=keyboard
    )


@router.callback_query(F.data == "child_balance")
async def show_balance(callback_query: types.CallbackQuery):
    """
    Показать баланс ребёнка.
    
    TODO: Интеграция с API для получения реального баланса.
    """
    await callback_query.answer()
    
    balance_text = (
        "🪙 <b>Твой баланс</b>\n\n"
        "Очки: <code>0</code> ⭐️\n"
        "Монеты: <code>0</code> 🪙\n\n"
        "Выполняй задания, чтобы зарабатывать больше!"
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="back_to_child_menu"
                )
            ]
        ]
    )
    
    await callback_query.message.edit_text(
        text=balance_text,
        reply_markup=keyboard
    )


@router.callback_query(F.data == "child_inventory")
async def show_inventory(callback_query: types.CallbackQuery):
    """
    Показать инвентарь ребёнка (купленные товары).
    
    TODO: Интеграция с API для получения списка покупок.
    """
    await callback_query.answer()
    
    inventory_text = (
        "🎒 <b>Мои покупки</b>\n\n"
        "У тебя пока нет покупок.\n"
        "Заработай монеты и купи что-нибудь в магазине!"
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛒 Магазин",
                    callback_data="child_shop"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="back_to_child_menu"
                )
            ]
        ]
    )
    
    await callback_query.message.edit_text(
        text=inventory_text,
        reply_markup=keyboard
    )


@router.callback_query(F.data == "child_tasks")
async def show_tasks(callback_query: types.CallbackQuery):
    """
    Показать задания ребёнка.
    
    TODO: Интеграция с API.
    """
    await callback_query.answer()
    
    tasks_text = (
        "📋 <b>Мои задания</b>\n\n"
        "Задания доступны через веб-приложение.\n"
        "Там ты можешь:\n"
        "• Просматривать активные задания\n"
        "• Сдавать выполненные задачи\n"
        "• Отслеживать прогресс"
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="back_to_child_menu"
                )
            ]
        ]
    )
    
    await callback_query.message.edit_text(
        text=tasks_text,
        reply_markup=keyboard
    )


@router.callback_query(F.data == "back_to_child_menu")
async def back_to_child_menu(callback_query: types.CallbackQuery):
    """Вернуться в меню ребёнка."""
    await callback_query.answer()
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📋 Мои задания",
                    callback_data="child_tasks"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🪙 Баланс",
                    callback_data="child_balance"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🛒 Магазин",
                    callback_data="child_shop"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎒 Мои покупки",
                    callback_data="child_inventory"
                )
            ]
        ]
    )
    
    menu_text = (
        "👶 <b>Меню ребёнка</b>\n\n"
        "Выберите действие:"
    )
    
    await callback_query.message.edit_text(
        text=menu_text,
        reply_markup=keyboard
    )
