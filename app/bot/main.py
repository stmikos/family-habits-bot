# Purpose: Telegram Bot main entry point and dispatcher setup.
# Context: aiogram 3.x Bot with FSM for creating tasks.
# Requirements: /start, role detection, MiniApp button, task creation FSM.

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.core.config import settings
from app.bot.handlers import start_router, tasks_router, admin_router, webapp_router
from app.bot.middlewares import DatabaseMiddleware, AuthMiddleware
from app.core import get_logger

logger = get_logger(__name__)


async def create_bot() -> Bot:
    """Создать и настроить Telegram Bot."""
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.HTML)
    return bot


async def create_dispatcher() -> Dispatcher:
    """Создать и настроить Dispatcher с middleware и handlers."""
    # FSM storage
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Middleware
    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    
    # Routers
    dp.include_router(webapp_router)
    dp.include_router(start_router)
    dp.include_router(tasks_router)
    dp.include_router(admin_router)
    
    return dp


async def main():
    """Основная функция запуска бота."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    bot = await create_bot()
    dp = await create_dispatcher()
    
    logger.info("Bot starting...")
    
    try:
        # Удаляем webhook на всякий случай
        await bot.delete_webhook(drop_pending_updates=True)
        # Запуск polling
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())