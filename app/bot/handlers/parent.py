# Purpose: Хендлеры для родителей - создание и модерация задач.
# Context: Parent-specific bot functionality, task management, notifications.
# Requirements: Task creation, approval/rejection, family management.

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from app.core import get_logger

logger = get_logger(__name__)
router = Router()


class TaskCreationStates(StatesGroup):
    """Состояния для создания задания."""
    waiting_for_child = State()
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_type = State()
    waiting_for_points = State()
    waiting_for_coins = State()
    waiting_for_confirmation = State()


@router.message(Command("parent"))
async def parent_menu(message: types.Message):
    """
    Главное меню для родителей.
    """
    user = message.from_user
    logger.info(f"Parent menu requested by user {user.id}")
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Создать задание",
                    callback_data="parent_create_task"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📋 Задания на проверку",
                    callback_data="parent_review_tasks"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👶 Управление детьми",
                    callback_data="parent_manage_children"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Статистика",
                    callback_data="parent_stats"
                )
            ]
        ]
    )
    
    menu_text = (
        "👨‍👩‍👧‍👦 <b>Меню родителя</b>\n\n"
        "Выберите действие:"
    )
    
    await message.answer(text=menu_text, reply_markup=keyboard)


@router.callback_query(F.data == "parent_create_task")
async def start_task_creation(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Начать создание задания.
    
    TODO: Получить список детей из API.
    """
    await callback_query.answer()
    
    # Пока используем заглушку
    await callback_query.message.answer(
        "➕ <b>Создание задания</b>\n\n"
        "Введите название задания:\n"
        "(например: <i>Помыть посуду</i>)"
    )
    
    await state.set_state(TaskCreationStates.waiting_for_title)


@router.message(TaskCreationStates.waiting_for_title)
async def process_task_title(message: types.Message, state: FSMContext):
    """Обработать название задания."""
    title = message.text.strip()
    
    if len(title) < 3:
        await message.answer(
            "❌ Название слишком короткое. Минимум 3 символа.\n"
            "Попробуйте ещё раз:"
        )
        return
    
    if len(title) > 120:
        await message.answer(
            "❌ Название слишком длинное. Максимум 120 символов.\n"
            "Попробуйте ещё раз:"
        )
        return
    
    await state.update_data(title=title)
    
    await message.answer(
        f"✅ Название: <b>{title}</b>\n\n"
        "Теперь введите описание задания:\n"
        "(например: <i>Помыть всю посуду после ужина и протереть стол</i>)"
    )
    
    await state.set_state(TaskCreationStates.waiting_for_description)


@router.message(TaskCreationStates.waiting_for_description)
async def process_task_description(message: types.Message, state: FSMContext):
    """Обработать описание задания."""
    description = message.text.strip()
    
    await state.update_data(description=description)
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📝 Текст", callback_data="task_type_text"),
                InlineKeyboardButton(text="📸 Фото", callback_data="task_type_photo")
            ],
            [
                InlineKeyboardButton(text="🎥 Видео", callback_data="task_type_video")
            ]
        ]
    )
    
    await message.answer(
        "Выберите тип отчёта о выполнении:",
        reply_markup=keyboard
    )
    
    await state.set_state(TaskCreationStates.waiting_for_type)


@router.callback_query(F.data.startswith("task_type_"))
async def process_task_type(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработать тип задания."""
    task_type = callback_query.data.replace("task_type_", "")
    await state.update_data(type=task_type)
    
    await callback_query.answer()
    
    type_emoji = {"text": "📝", "photo": "📸", "video": "🎥"}
    
    await callback_query.message.answer(
        f"✅ Тип отчёта: {type_emoji.get(task_type, '')} {task_type}\n\n"
        "Введите количество очков за выполнение (1-100):\n"
        "(рекомендуется: 5-10 для простых заданий)"
    )
    
    await state.set_state(TaskCreationStates.waiting_for_points)


@router.message(TaskCreationStates.waiting_for_points)
async def process_task_points(message: types.Message, state: FSMContext):
    """Обработать очки за задание."""
    try:
        points = int(message.text.strip())
        
        if points < 1 or points > 100:
            await message.answer(
                "❌ Очки должны быть от 1 до 100.\n"
                "Попробуйте ещё раз:"
            )
            return
        
        await state.update_data(points=points)
        
        await message.answer(
            f"✅ Очки: <b>{points}</b> ⭐️\n\n"
            "Введите количество монет за выполнение (0-100):\n"
            "(монеты можно потратить в магазине)"
        )
        
        await state.set_state(TaskCreationStates.waiting_for_coins)
        
    except ValueError:
        await message.answer(
            "❌ Введите число от 1 до 100.\n"
            "Попробуйте ещё раз:"
        )


@router.message(TaskCreationStates.waiting_for_coins)
async def process_task_coins(message: types.Message, state: FSMContext):
    """Обработать монеты за задание."""
    try:
        coins = int(message.text.strip())
        
        if coins < 0 or coins > 100:
            await message.answer(
                "❌ Монеты должны быть от 0 до 100.\n"
                "Попробуйте ещё раз:"
            )
            return
        
        await state.update_data(coins=coins)
        
        # Показываем сводку и просим подтверждения
        data = await state.get_data()
        
        type_emoji = {"text": "📝", "photo": "📸", "video": "🎥"}
        task_type = data.get("type", "text")
        
        summary = (
            "📋 <b>Проверьте задание:</b>\n\n"
            f"<b>Название:</b> {data['title']}\n"
            f"<b>Описание:</b> {data['description']}\n"
            f"<b>Тип:</b> {type_emoji.get(task_type, '')} {task_type}\n"
            f"<b>Очки:</b> {data['points']} ⭐️\n"
            f"<b>Монеты:</b> {coins} 🪙\n\n"
            "Всё верно?"
        )
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Создать", callback_data="task_confirm"),
                    InlineKeyboardButton(text="❌ Отменить", callback_data="task_cancel")
                ]
            ]
        )
        
        await message.answer(summary, reply_markup=keyboard)
        await state.set_state(TaskCreationStates.waiting_for_confirmation)
        
    except ValueError:
        await message.answer(
            "❌ Введите число от 0 до 100.\n"
            "Попробуйте ещё раз:"
        )


@router.callback_query(F.data == "task_confirm")
async def confirm_task_creation(callback_query: types.CallbackQuery, state: FSMContext):
    """Подтвердить создание задания."""
    await callback_query.answer()
    
    data = await state.get_data()
    
    # TODO: Отправить задание через API
    logger.info(f"Task created by user {callback_query.from_user.id}: {data}")
    
    await callback_query.message.answer(
        "✅ <b>Задание создано!</b>\n\n"
        "Ребёнок получит уведомление о новом задании.\n"
        "Вы увидите его в списке для проверки, как только ребёнок выполнит задание."
    )
    
    await state.clear()


@router.callback_query(F.data == "task_cancel")
async def cancel_task_creation(callback_query: types.CallbackQuery, state: FSMContext):
    """Отменить создание задания."""
    await callback_query.answer()
    await callback_query.message.answer("❌ Создание задания отменено.")
    await state.clear()


@router.callback_query(F.data == "parent_review_tasks")
async def review_tasks(callback_query: types.CallbackQuery):
    """
    Показать задания на проверку.
    
    TODO: Интеграция с API.
    """
    await callback_query.answer()
    
    tasks_text = (
        "📋 <b>Задания на проверку</b>\n\n"
        "Нет заданий на проверку.\n\n"
        "Когда ребёнок выполнит задание, оно появится здесь."
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="back_to_parent_menu"
                )
            ]
        ]
    )
    
    await callback_query.message.edit_text(
        text=tasks_text,
        reply_markup=keyboard
    )


@router.callback_query(F.data == "parent_manage_children")
async def manage_children(callback_query: types.CallbackQuery):
    """
    Управление детьми.
    
    TODO: Интеграция с API.
    """
    await callback_query.answer()
    
    children_text = (
        "👶 <b>Управление детьми</b>\n\n"
        "Эта функция доступна через веб-приложение.\n"
        "Там вы можете:\n"
        "• Добавлять детей\n"
        "• Редактировать профили\n"
        "• Просматривать статистику"
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="back_to_parent_menu"
                )
            ]
        ]
    )
    
    await callback_query.message.edit_text(
        text=children_text,
        reply_markup=keyboard
    )


@router.callback_query(F.data == "parent_stats")
async def show_stats(callback_query: types.CallbackQuery):
    """
    Показать статистику.
    
    TODO: Интеграция с API.
    """
    await callback_query.answer()
    
    stats_text = (
        "📊 <b>Статистика семьи</b>\n\n"
        "Эта функция доступна через веб-приложение."
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="back_to_parent_menu"
                )
            ]
        ]
    )
    
    await callback_query.message.edit_text(
        text=stats_text,
        reply_markup=keyboard
    )


@router.callback_query(F.data == "back_to_parent_menu")
async def back_to_parent_menu(callback_query: types.CallbackQuery):
    """Вернуться в меню родителя."""
    await callback_query.answer()
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Создать задание",
                    callback_data="parent_create_task"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📋 Задания на проверку",
                    callback_data="parent_review_tasks"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👶 Управление детьми",
                    callback_data="parent_manage_children"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Статистика",
                    callback_data="parent_stats"
                )
            ]
        ]
    )
    
    menu_text = (
        "👨‍👩‍👧‍👦 <b>Меню родителя</b>\n\n"
        "Выберите действие:"
    )
    
    await callback_query.message.edit_text(
        text=menu_text,
        reply_markup=keyboard
    )
