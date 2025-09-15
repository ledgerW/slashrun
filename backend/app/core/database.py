from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlmodel import SQLModel
from .config import settings


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


# Create async engine with configuration from settings
# Only apply pool settings for PostgreSQL, not SQLite
engine_kwargs = {"echo": settings.database_echo}

if not settings.database_url.startswith("sqlite"):
    # PostgreSQL-specific pool settings
    engine_kwargs.update({
        "pool_size": settings.database_settings.pool_size,
        "max_overflow": settings.database_settings.max_overflow,
        "pool_timeout": settings.database_settings.pool_timeout,
        "pool_recycle": settings.database_settings.pool_recycle,
    })

engine = create_async_engine(settings.database_url, **engine_kwargs)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database by creating all tables.
    
    This should be called once during application startup.
    """
    async with engine.begin() as conn:
        # Import all models here to ensure they are registered
        from ..models import scenario, audit, trigger  # noqa
        
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db() -> None:
    """
    Close database engine and all connections.
    
    This should be called during application shutdown.
    """
    await engine.dispose()
