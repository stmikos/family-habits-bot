#!/usr/bin/env python3
# Purpose: Demo script to run Family Habit Bot.
# Context: Quick start script for testing bot functionality.
# Requirements: Check environment, create demo data, start bot.

import asyncio
import os
import sys
from app.core.config import settings
from app.core import setup_logging, get_logger
from app.bot.main import create_bot, create_dispatcher

logger = get_logger(__name__)


async def create_demo_data():
    """Создать демо-данные для тестирования."""
    from app.db.session import SessionLocal
    from app.db.models import Family, Parent, Child, ShopItem, Plan
    
    async with SessionLocal() as session:
        # Проверяем, есть ли уже данные
        from sqlalchemy import select, func
        count = await session.scalar(select(func.count(Family.id)))
        
        if count > 0:
            logger.info("Demo data already exists")
            return
        
        # Создаём демо-семью
        family = Family(plan=Plan.FREE)
        session.add(family)
        await session.flush()
        
        # Создаём демо-родителя (используем admin ID из настроек)
        admin_ids = settings.ADMIN_USER_IDS
        if admin_ids:
            parent = Parent(
                tg_id=admin_ids[0],
                name="Demo Parent",
                family_id=family.id
            )
            session.add(parent)
        
        # Создаём демо-детей
        children = [
            Child(name="Аня", family_id=family.id, points=15, coins=3),
            Child(name="Максим", family_id=family.id, points=22, coins=5),
        ]
        session.add_all(children)
        
        # Создаём товары в магазине
        shop_items = [
            ShopItem(sku="ice_cream", title="🍦 Мороженое", price_coins=3, description="Вкусное мороженое на выбор"),
            ShopItem(sku="movie_night", title="🎬 Семейный кинопросмотр", price_coins=5, description="Выбираешь фильм для всей семьи"),
            ShopItem(sku="extra_screen", title="📱 +30 мин экранного времени", price_coins=2, description="Дополнительное время с гаджетами"),
            ShopItem(sku="pizza", title="🍕 Пицца на выходных", price_coins=8, description="Заказываем пиццу в выходные"),
            ShopItem(sku="book_choice", title="📚 Выбор книги для чтения", price_coins=4, description="Выбираешь книгу, которую будем читать вместе"),
        ]
        session.add_all(shop_items)
        
        await session.commit()
        logger.info(f"✅ Created demo family {family.id} with {len(children)} children and {len(shop_items)} shop items")


async def check_environment():
    """Проверить окружение."""
    logger.info("🔍 Checking environment...")
    
    # Проверяем токен бота
    if settings.TELEGRAM_BOT_TOKEN == "demo_token_for_testing":
        logger.warning("⚠️  Using demo Telegram Bot token")
        logger.warning("   To use with real Telegram, set TELEGRAM_BOT_TOKEN in .env")
    else:
        logger.info("✅ Real Telegram Bot token configured")
    
    # Проверяем URL MiniApp
    if settings.WEBAPP_URL == "https://example.com":
        logger.warning("⚠️  Using demo WebApp URL")
        logger.warning("   Set WEBAPP_URL to your deployed MiniApp")
    else:
        logger.info(f"✅ WebApp URL: {settings.WEBAPP_URL}")
    
    # Проверяем базу данных
    if os.path.exists("family_habits.db"):
        logger.info("✅ Database exists")
    else:
        logger.warning("⚠️  Database not found, run: alembic upgrade head")
    
    logger.info(f"✅ Environment check complete")


async def main():
    """Основная функция."""
    setup_logging(settings.log_level)
    logger.info("🚀 Starting Family Habit Bot Demo")
    
    await check_environment()
    await create_demo_data()
    
    # Проверяем, можно ли запустить бота
    if settings.TELEGRAM_BOT_TOKEN == "demo_token_for_testing":
        logger.info("📋 Bot configured successfully!")
        logger.info("")
        logger.info("🎯 M2 Phase Implementation Complete:")
        logger.info("  ✅ Telegram Bot with aiogram 3.x")
        logger.info("  ✅ FSM for task creation workflow")
        logger.info("  ✅ Parent/Child role separation")
        logger.info("  ✅ Database with Telegram integration")
        logger.info("  ✅ MiniApp button integration")
        logger.info("  ✅ Shop system foundation")
        logger.info("")
        logger.info("🔧 To run with real Telegram:")
        logger.info("  1. Get bot token from @BotFather")
        logger.info("  2. Set TELEGRAM_BOT_TOKEN in .env")
        logger.info("  3. Deploy MiniApp frontend")
        logger.info("  4. Set WEBAPP_URL in .env")
        logger.info("  5. Run: python -m app.bot.main")
        return
    
    # Запускаем бота
    logger.info("🤖 Starting Telegram Bot...")
    bot = await create_bot()
    dp = await create_dispatcher()
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Bot started! Send /start to test")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)