# Purpose: Database session management.
# Context: AsyncSession for async operations.
# Requirements: Database connection, dependency injection.

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings

# Создаём async engine
engine = create_async_engine(
    settings.database_url,
    poolclass=StaticPool,
    echo=settings.log_level == "DEBUG"
)

# Session factory
SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_session() -> AsyncSession:
    """Dependency для получения database session."""
    async with SessionLocal() as session:
        yield session