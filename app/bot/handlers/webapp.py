"""
Handlers for Telegram WebApp integration
"""
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.db.models import Parent, Child, Family
from aiogram.fsm.context import FSMContext
import os
import logging

logger = logging.getLogger(__name__)

webapp_router = Router()

# URL вашего веб-приложения
WEBAPP_URL = os.getenv("WEBAPP_URL", "http://localhost:8000")

@webapp_router.message(Command("app", "webapp", "start"))
async def cmd_webapp(message: Message, session: AsyncSession, state: FSMContext):
    """Открыть веб-приложение Family Habits"""
    
    # Проверяем, есть ли пользователь в базе
    parent = await session.get(Parent, message.from_user.id)
    
    if not parent:
        # Новый пользователь - начинаем регистрацию
        webapp_url = f"{WEBAPP_URL}/registration.html?user_id={message.from_user.id}&first_name={message.from_user.first_name}"
        button_text = "🌱 Начать семейный путь"
        welcome_text = f"🌟 Добро пожаловать, {message.from_user.first_name}!\n\n" \
                      f"Хабит и Хабби готовы помочь вашей семье развивать полезные привычки! 🌿\n\n" \
                      f"Нажмите кнопку ниже, чтобы создать семейный профиль и начать увлекательное путешествие к лучшим привычкам! 🚀"
    else:
        # Существующий пользователь - переходим к главной странице
        family = await session.get(Family, parent.family_id) if parent.family_id else None
        webapp_url = f"{WEBAPP_URL}/index.html?user_id={message.from_user.id}&family_id={parent.family_id if family else ''}"
        button_text = "🏠 Открыть Family Habits"
        welcome_text = f"🎉 С возвращением, {parent.name}!\n\n" \
                      f"Ваша семья '{family.name if family else 'Личный профиль'}' ждет вас! 👨‍👩‍👧‍👦\n\n" \
                      f"Готовы продолжить развивать полезные привычки? 💪"

    # Создаем клавиатуру с WebApp кнопкой
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=button_text,
                    web_app=WebAppInfo(url=webapp_url)
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ О приложении",
                    callback_data="about_app"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🆘 Помощь",
                    callback_data="help_app"
                )
            ]
        ]
    )

    await message.answer(
        text=welcome_text,
        reply_markup=keyboard
    )

@webapp_router.message(Command("family"))
async def cmd_family_dashboard(message: Message, session: AsyncSession):
    """Открыть семейную панель управления"""
    
    parent = await session.get(Parent, message.from_user.id)
    if not parent or not parent.family_id:
        await message.answer(
            "❌ Сначала создайте семейный профиль!\n\n"
            "Используйте команду /app для начала работы."
        )
        return

    family = await session.get(Family, parent.family_id)
    webapp_url = f"{WEBAPP_URL}/index.html?user_id={message.from_user.id}&family_id={parent.family_id}&tab=family"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👨‍👩‍👧‍👦 Семейная панель",
                    web_app=WebAppInfo(url=webapp_url)
                )
            ]
        ]
    )

    await message.answer(
        f"🏠 Семья '{family.name}'\n\n"
        f"👥 Участников: {len(family.children) + 1 if family.children else 1}\n"
        f"⭐ Общие баллы: {sum(child.points for child in family.children) if family.children else 0}\n\n"
        f"Откройте семейную панель для управления задачами и прогрессом! 📊",
        reply_markup=keyboard
    )

@webapp_router.message(Command("tasks"))
async def cmd_tasks(message: Message, session: AsyncSession):
    """Открыть страницу создания задач"""
    
    parent = await session.get(Parent, message.from_user.id)
    if not parent:
        await cmd_webapp(message, session, None)
        return

    webapp_url = f"{WEBAPP_URL}/create-task.html?user_id={message.from_user.id}&family_id={parent.family_id or ''}"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Создать задачу",
                    web_app=WebAppInfo(url=webapp_url)
                )
            ]
        ]
    )

    await message.answer(
        "🎯 Создание новой задачи\n\n"
        "Хабит и Хабби помогут вам создать интересную и полезную задачу для вашей семьи! 🌟\n\n"
        "Выберите тип задачи, сложность, награды и многое другое! 🎁",
        reply_markup=keyboard
    )

@webapp_router.message(Command("shop"))
async def cmd_shop(message: Message, session: AsyncSession):
    """Открыть магазин наград"""
    
    parent = await session.get(Parent, message.from_user.id)
    if not parent:
        await cmd_webapp(message, session, None)
        return

    webapp_url = f"{WEBAPP_URL}/shop.html?user_id={message.from_user.id}&stars=0"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛍️ Открыть магазин",
                    web_app=WebAppInfo(url=webapp_url)
                )
            ]
        ]
    )

    await message.answer(
        f"🛒 Магазин наград\n\n"
        f"💰 Ваш баланс: 0 ⭐ (демо)\n\n"
        f"Хабит и Хабби открыли волшебный магазин с наградами за ваши достижения! 🎁\n\n"
        f"Покупайте привилегии, лакомства и семейные развлечения! 🎉",
        reply_markup=keyboard
    )

@webapp_router.message(Command("profile"))
async def cmd_profile(message: Message, session: AsyncSession):
    """Открыть профиль пользователя"""
    
    parent = await session.get(Parent, message.from_user.id)
    if not parent:
        await cmd_webapp(message, session, None)
        return

    webapp_url = f"{WEBAPP_URL}/profile.html?user_id={message.from_user.id}"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👤 Мой профиль",
                    web_app=WebAppInfo(url=webapp_url)
                )
            ]
        ]
    )

    await message.answer(
        f"👤 Профиль: {parent.name or 'Родитель'}\n\n"
        f"⭐ Баллы: 0 (демо)\n"
        f"🏆 Статус: Родитель\n"
        f"👨‍👩‍👧‍� Семья: {family.name if parent.family_id else 'Не указана'}\n\n"
        f"Просмотрите свой прогресс, достижения и настройки! 📊",
        reply_markup=keyboard
    )

@webapp_router.message(Command("stats"))
async def cmd_statistics(message: Message, session: AsyncSession):
    """Открыть статистику"""
    
    parent = await session.get(Parent, message.from_user.id)
    if not parent:
        await cmd_webapp(message, session, None)
        return

    webapp_url = f"{WEBAPP_URL}/statistics.html?user_id={message.from_user.id}&family_id={parent.family_id or ''}"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 Статистика",
                    web_app=WebAppInfo(url=webapp_url)
                )
            ]
        ]
    )

    await message.answer(
        "📈 Статистика и аналитика\n\n"
        "Хабит и Хабби проанализировали вашу активность и готовы показать подробную статистику! 📊\n\n"
        "• Графики прогресса 📈\n"
        "• Семейный рейтинг 🏆\n"
        "• Инсайты и рекомендации 💡\n"
        "• Прогресс по целям 🎯",
        reply_markup=keyboard
    )

@webapp_router.callback_query(F.data == "about_app")
async def callback_about_app(callback):
    """Информация о приложении"""
    await callback.message.edit_text(
        "🌱 **Family Habits** - семейный трекер привычек\n\n"
        "🎯 **Что мы делаем:**\n"
        "• Помогаем семьям развивать полезные привычки\n"
        "• Мотивируем через игровые элементы\n"
        "• Создаем позитивную атмосферу роста\n\n"
        "🌟 **Особенности:**\n"
        "• Персональные задачи для каждого\n"
        "• Система наград и достижений\n"
        "• Семейная статистика и прогресс\n"
        "• Талисманы Хабит и Хабби\n\n"
        "🚀 **Начните прямо сейчас:** /app",
        parse_mode="Markdown"
    )

@webapp_router.callback_query(F.data == "help_app")
async def callback_help_app(callback):
    """Помощь по использованию"""
    await callback.message.edit_text(
        "🆘 **Помощь по Family Habits**\n\n"
        "📱 **Основные команды:**\n"
        "• `/app` - Открыть приложение\n"
        "• `/family` - Семейная панель\n"
        "• `/tasks` - Создать задачу\n"
        "• `/shop` - Магазин наград\n"
        "• `/profile` - Мой профиль\n"
        "• `/stats` - Статистика\n\n"
        "💡 **Как использовать:**\n"
        "1. Создайте семейный профиль\n"
        "2. Добавьте детей и задачи\n"
        "3. Отмечайте выполнение\n"
        "4. Получайте звезды и награды\n\n"
        "❓ **Нужна помощь?** Напишите /support",
        parse_mode="Markdown"
    )

@webapp_router.message(Command("support"))
async def cmd_support(message: Message):
    """Техническая поддержка"""
    await message.answer(
        "🛠️ **Техническая поддержка**\n\n"
        "Если у вас возникли проблемы или вопросы:\n\n"
        "📧 Email: support@familyhabits.com\n"
        "💬 Telegram: @family_habits_support\n"
        "🌐 Сайт: https://familyhabits.com\n\n"
        "⏰ Время ответа: до 24 часов\n\n"
        "Хабит и Хабби всегда готовы помочь! 🌟",
        parse_mode="Markdown"
    )