# Purpose: Task management handlers with FSM.
# Context: Создание заданий через диалог, просмотр заданий.
# Requirements: FSM для создания задач, кнопки для Parent/Child.

from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import Parent, Child, Task, TaskType, TaskStatus
from app.services.parent_service import ParentService
from app.services.task_service import TaskService
from app.core import get_logger

router = Router()
logger = get_logger(__name__)


class TaskCreationStates(StatesGroup):
    """FSM состояния для создания задания."""
    waiting_for_child = State()
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_type = State()
    waiting_for_points = State()
    waiting_for_coins = State()


@router.message(lambda message: message.text == "📝 Создать задание")
async def create_task_start(message: types.Message, state: FSMContext, session: AsyncSession):
    """Начало создания задания."""
    user_id = message.from_user.id
    
    # Проверяем, что это родитель
    parent_service = ParentService(session)
    parent = await parent_service.get_parent_by_tg_id(user_id)
    
    if not parent:
        await message.answer("❌ Только родители могут создавать задания")
        return
    
    # Получаем детей
    children = await parent_service.get_children(parent.id)
    
    if not children:
        await message.answer(
            "👥 Сначала нужно добавить детей!\n\n"
            "📱 Попросите ребёнка написать боту /start для регистрации"
        )
        return
    
    # Создаём клавиатуру с детьми
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"👦👧 {child.name}", callback_data=f"child_{child.id}")]
        for child in children
    ] + [[InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_task")]])
    
    await message.answer(
        "👨‍👩‍👧‍👦 <b>Для кого создаём задание?</b>\n\n"
        "Выберите ребёнка из списка:",
        reply_markup=keyboard
    )
    
    await state.set_state(TaskCreationStates.waiting_for_child)


@router.callback_query(StateFilter(TaskCreationStates.waiting_for_child), F.data.startswith("child_"))
async def child_selected(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    """Ребёнок выбран."""
    child_id = int(callback.data.split("_")[1])
    
    # Сохраняем ID ребёнка
    await state.update_data(child_id=child_id)
    
    # Получаем имя ребёнка
    child = await session.get(Child, child_id)
    if not child:
        await callback.answer("❌ Ребёнок не найден")
        return
    
    await callback.message.edit_text(
        f"📝 <b>Создание задания для {child.name}</b>\n\n"
        f"📋 Введите название задания:\n"
        f"<i>Например: \"Убрать комнату\", \"Сделать домашнее задание\"</i>"
    )
    
    await state.set_state(TaskCreationStates.waiting_for_title)
    await callback.answer()


@router.message(StateFilter(TaskCreationStates.waiting_for_title))
async def title_received(message: types.Message, state: FSMContext):
    """Получено название задания."""
    title = message.text.strip()
    
    if len(title) < 3:
        await message.answer("❌ Название должно быть минимум 3 символа")
        return
    
    if len(title) > 120:
        await message.answer("❌ Название слишком длинное (максимум 120 символов)")
        return
    
    await state.update_data(title=title)
    
    await message.answer(
        f"✅ Название: <b>{title}</b>\n\n"
        f"📝 Теперь введите описание задания:\n"
        f"<i>Подробно опишите, что нужно сделать</i>"
    )
    
    await state.set_state(TaskCreationStates.waiting_for_description)


@router.message(StateFilter(TaskCreationStates.waiting_for_description))
async def description_received(message: types.Message, state: FSMContext):
    """Получено описание задания."""
    description = message.text.strip()
    
    if len(description) < 5:
        await message.answer("❌ Описание должно быть минимум 5 символов")
        return
    
    await state.update_data(description=description)
    
    # Клавиатура с типами заданий
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Текст", callback_data="type_text")],
        [InlineKeyboardButton(text="📸 Фото", callback_data="type_photo")],
        [InlineKeyboardButton(text="🎥 Видео", callback_data="type_video")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_task")]
    ])
    
    await message.answer(
        f"✅ Описание добавлено\n\n"
        f"🎯 <b>Как ребёнок должен подтвердить выполнение?</b>",
        reply_markup=keyboard
    )
    
    await state.set_state(TaskCreationStates.waiting_for_type)


@router.callback_query(StateFilter(TaskCreationStates.waiting_for_type), F.data.startswith("type_"))
async def type_selected(callback: types.CallbackQuery, state: FSMContext):
    """Тип задания выбран."""
    task_type = callback.data.split("_")[1]
    await state.update_data(type=task_type)
    
    type_emojis = {"text": "📝", "photo": "📸", "video": "🎥"}
    type_names = {"text": "Текст", "photo": "Фото", "video": "Видео"}
    
    await callback.message.edit_text(
        f"✅ Тип: {type_emojis[task_type]} {type_names[task_type]}\n\n"
        f"⭐ <b>Сколько очков дать за выполнение?</b>\n"
        f"<i>Введите число от 1 до 100</i>"
    )
    
    await state.set_state(TaskCreationStates.waiting_for_points)
    await callback.answer()


@router.message(StateFilter(TaskCreationStates.waiting_for_points))
async def points_received(message: types.Message, state: FSMContext):
    """Получены очки."""
    try:
        points = int(message.text.strip())
        if points < 1 or points > 100:
            raise ValueError()
    except ValueError:
        await message.answer("❌ Введите число от 1 до 100")
        return
    
    await state.update_data(points=points)
    
    await message.answer(
        f"✅ Очки: <b>{points}</b>\n\n"
        f"🪙 <b>Сколько монет дать за выполнение?</b>\n"
        f"<i>Введите число от 0 до 100 (0 = без монет)</i>"
    )
    
    await state.set_state(TaskCreationStates.waiting_for_coins)


@router.message(StateFilter(TaskCreationStates.waiting_for_coins))
async def coins_received(message: types.Message, state: FSMContext, session: AsyncSession):
    """Получены монеты - завершение создания."""
    try:
        coins = int(message.text.strip())
        if coins < 0 or coins > 100:
            raise ValueError()
    except ValueError:
        await message.answer("❌ Введите число от 0 до 100")
        return
    
    # Получаем данные из FSM
    data = await state.get_data()
    user_id = message.from_user.id
    
    # Получаем родителя
    parent_service = ParentService(session)
    parent = await parent_service.get_parent_by_tg_id(user_id)
    
    # Создаём задание
    task = Task(
        title=data["title"],
        description=data["description"],
        type=TaskType(data["type"]),
        points=data["points"],
        coins=coins,
        child_id=data["child_id"],
        parent_id=parent.id,
        status=TaskStatus.new
    )
    
    session.add(task)
    await session.commit()
    await session.refresh(task)
    
    # Получаем ребёнка для уведомления
    child = await session.get(Child, data["child_id"])
    
    type_emojis = {"text": "📝", "photo": "📸", "video": "🎥"}
    
    await message.answer(
        f"✅ <b>Задание создано!</b>\n\n"
        f"👦👧 Для: <b>{child.name}</b>\n"
        f"📋 Задание: <b>{data['title']}</b>\n"
        f"📝 Описание: {data['description']}\n"
        f"🎯 Тип: {type_emojis[data['type']]}\n"
        f"⭐ Очки: <b>{data['points']}</b>\n"
        f"🪙 Монеты: <b>{coins}</b>\n\n"
        f"🔔 Ребёнок получит уведомление о новом задании!"
    )
    
    # Уведомляем ребёнка (если у него есть tg_id)
    if child.tg_id:
        try:
            await message.bot.send_message(
                child.tg_id,
                f"🎯 <b>Новое задание!</b>\n\n"
                f"📋 {data['title']}\n"
                f"📝 {data['description']}\n\n"
                f"⭐ За выполнение: <b>{data['points']} очков</b>\n"
                f"🪙 Монеты: <b>{coins}</b>\n\n"
                f"🎮 Открой приложение для выполнения!"
            )
        except Exception as e:
            logger.warning(f"Failed to notify child {child.id}: {e}")
    
    await state.clear()
    logger.info(f"Task created: {task.id} for child {child.id} by parent {parent.id}")


@router.callback_query(F.data == "cancel_task")
async def cancel_task_creation(callback: types.CallbackQuery, state: FSMContext):
    """Отмена создания задания."""
    await callback.message.edit_text("❌ Создание задания отменено")
    await state.clear()
    await callback.answer()