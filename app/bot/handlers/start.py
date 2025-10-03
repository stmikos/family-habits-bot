# Purpose: /start handler and role detection.
# Context: Регистрация пользователей, роли Parent/Child, MiniApp кнопка.
# Requirements: Автосоздание Parent, определение роли, главное меню.

from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Parent, Child
from app.services.parent_service import ParentService
from app.core.config import settings
from app.core import get_logger

router = Router()
logger = get_logger(__name__)


def get_main_keyboard(role: str) -> ReplyKeyboardMarkup:
    """Получить главную клавиатуру в зависимости от роли."""
    if role == "parent":
        webapp_url = f"{settings.WEBAPP_URL}/parent"
        buttons = [
            [KeyboardButton(text="🏠 Семейная панель", web_app=WebAppInfo(url=webapp_url))],
            [KeyboardButton(text="📝 Создать задание")],
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="👨‍👩‍👧‍👦 Дети")]
        ]
    else:  # child
        webapp_url = f"{settings.WEBAPP_URL}/child"
        buttons = [
            [KeyboardButton(text="🎮 Мои задания", web_app=WebAppInfo(url=webapp_url))],
            [KeyboardButton(text="🏆 Мои очки"), KeyboardButton(text="🛒 Магазин")]
        ]
    
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


@router.message(CommandStart())
async def start_handler(message: types.Message, session: AsyncSession):
    """Обработка команды /start."""
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or ""
    
    # Проверяем, существует ли пользователь как родитель
    parent_service = ParentService(session)
    parent = await parent_service.get_parent_by_tg_id(user_id)
    
    if parent:
        # Существующий родитель
        keyboard = get_main_keyboard("parent")
        await message.answer(
            f"👋 С возвращением, {first_name}!\n\n"
            f"🏠 Добро пожаловать в Family Habit!\n"
            f"Управляйте заданиями для ваших детей и следите за их прогрессом.",
            reply_markup=keyboard
        )
        logger.info(f"Returning parent {user_id} ({username}) logged in")
        return
    
    # Проверяем, существует ли как ребёнок
    from sqlalchemy import select
    result = await session.execute(
        select(Child).where(Child.tg_id == user_id)
    )
    child = result.scalar_one_or_none()
    
    if child:
        # Существующий ребёнок
        keyboard = get_main_keyboard("child")
        await message.answer(
            f"👋 Привет, {child.name}! 🎉\n\n"
            f"🎮 Добро пожаловать в твои задания!\n"
            f"Выполняй задачи и получай очки! 🏆",
            reply_markup=keyboard
        )
        logger.info(f"Child {user_id} ({child.name}) logged in")
        return
    
    # Новый пользователь - регистрируем как родителя
    parent = await parent_service.create_parent(user_id, first_name)
    
    keyboard = get_main_keyboard("parent")
    await message.answer(
        f"🎉 Добро пожаловать в Family Habit, {first_name}!\n\n"
        f"👨‍👩‍👧‍👦 Вы зарегистрированы как <b>Родитель</b>\n\n"
        f"📝 Создавайте задания для детей\n"
        f"⭐ Одобряйте выполненные задачи\n"
        f"🏆 Следите за прогрессом семьи\n\n"
        f"💡 Начните с добавления детей в семью!",
        reply_markup=keyboard
    )
    
    logger.info(f"New parent registered: {user_id} ({username}) -> {parent.id}")


@router.message(lambda message: message.text == "👨‍👩‍👧‍👦 Дети")
async def children_handler(message: types.Message, session: AsyncSession):
    """Управление детьми."""
    user_id = message.from_user.id
    
    # Получаем родителя
    parent_service = ParentService(session)
    parent = await parent_service.get_parent_by_tg_id(user_id)
    
    if not parent:
        await message.answer("❌ Только родители могут управлять детьми")
        return
    
    # Получаем детей
    children = await parent_service.get_children(parent.id)
    
    if not children:
        await message.answer(
            "👥 У вас пока нет детей в системе\n\n"
            "🆔 Дети регистрируются автоматически при первом входе в бота\n"
            "📱 Попросите ребёнка написать боту /start"
        )
        return
    
    children_text = "\n".join([
        f"👦👧 {child.name} - {child.points} очков, {child.coins} монет"
        for child in children
    ])
    
    await message.answer(
        f"👨‍👩‍👧‍👦 <b>Ваши дети:</b>\n\n{children_text}\n\n"
        f"🎮 Используйте MiniApp для управления заданиями"
    )


@router.message(lambda message: message.text == "🏆 Мои очки")
async def my_points_handler(message: types.Message, session: AsyncSession):
    """Показать очки ребёнка."""
    user_id = message.from_user.id
    
    from sqlalchemy import select
    result = await session.execute(
        select(Child).where(Child.tg_id == user_id)
    )
    child = result.scalar_one_or_none()
    
    if not child:
        await message.answer("❌ Только дети могут просматривать свои очки")
        return
    
    await message.answer(
        f"🏆 <b>{child.name}, твои достижения:</b>\n\n"
        f"⭐ Очки: <b>{child.points}</b>\n"
        f"🪙 Монеты: <b>{child.coins}</b>\n\n"
        f"🎮 Выполняй задания и получай больше очков!"
    )