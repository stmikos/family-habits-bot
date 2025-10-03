# Purpose: Database session management and connection setup.
# Context: Async SQLAlchemy session factory with proper connection management.
# Requirements: Async engine, session factory, dependency injection for FastAPI.

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Создание async engine
engine = create_async_engine(
    settings.database_url,
    echo=not settings.is_production,
    poolclass=NullPool if settings.is_production else None,
    future=True
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения сессии БД в FastAPI.
    
    Yields:
        AsyncSession: Сессия базы данных.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Инициализация базы данных (создание таблиц)."""
    from app.db.models import Base
    
    async with engine.begin() as conn:
        # В продакшне используем Alembic, здесь только для разработки
        if not settings.is_production:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created")


async def close_db() -> None:
    """Закрытие соединений с БД."""
    await engine.dispose()
    logger.info("Database connections closed")