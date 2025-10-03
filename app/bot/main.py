# Purpose: Главный модуль Telegram-бота.
# Context: Entry point for aiogram bot with handlers, middleware, and FSM.
# Requirements: Load config, setup logging, register handlers, start polling.

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.core import setup_logging, get_logger, settings
from app.bot.handlers import start, parent, child

logger = get_logger(__name__)


async def main():
    """Запуск Telegram-бота."""
    setup_logging()
    logger.info("Starting Family Habit Bot")
    
    # Создаём бота и диспетчер
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )
    
    dp = Dispatcher()
    
    # Регистрируем роутеры
    dp.include_router(start.router)
    dp.include_router(parent.router)
    dp.include_router(child.router)
    
    # Запускаем поллинг
    try:
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        logger.error(f"Bot polling error: {e}")
    finally:
        await bot.session.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())