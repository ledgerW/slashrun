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
        from db.models import user, scenario, audit, trigger, state  # noqa
        
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)
    
    # Create default admin user for development
    await create_default_admin_user()


async def create_default_admin_user() -> None:
    """Create default admin user for development if it doesn't exist, or reset password if it does."""
    try:
        from ..services.user_service import user_service
        from ..services.auth_service import auth_service
        from datetime import datetime
        
        async with AsyncSessionLocal() as db:
            # Check if admin user already exists
            existing_user = await user_service.get_user_by_email(
                settings.default_admin_email, db
            )
            
            if not existing_user:
                # Create admin user
                await user_service.create_user(
                    email=settings.default_admin_email,
                    username=settings.default_admin_username,
                    password=settings.default_admin_password,
                    full_name="System Administrator",
                    organization="SlashRun",
                    position="Administrator",
                    db=db
                )
                print(f"Created default admin user: {settings.default_admin_email}")
            else:
                # Reset admin password to ensure it's correct for testing
                existing_user.hashed_password = auth_service.hash_password(settings.default_admin_password)
                existing_user.updated_at = datetime.utcnow()
                db.add(existing_user)
                await db.commit()
                print(f"Reset admin user password: {settings.default_admin_email}")
                
    except Exception as e:
        print(f"Warning: Could not create default admin user: {e}")
        # Don't fail startup if user creation fails


async def seed_development_data() -> None:
    """Seed database with development test data."""
    try:
        from ..services.user_service import user_service
        
        async with AsyncSessionLocal() as db:
            # Create test users if they don't exist
            test_users = [
                {
                    "email": "alice@example.com",
                    "username": "alice",
                    "password": "password123",
                    "full_name": "Alice Johnson",
                    "organization": "Economic Research Institute",
                    "position": "Senior Analyst"
                },
                {
                    "email": "bob@example.com", 
                    "username": "bob",
                    "password": "password123",
                    "full_name": "Bob Smith",
                    "organization": "Policy Think Tank",
                    "position": "Researcher"
                }
            ]
            
            for user_data in test_users:
                existing_user = await user_service.get_user_by_email(
                    user_data["email"], db
                )
                
                if not existing_user:
                    await user_service.create_user(**user_data, db=db)
                    print(f"Created test user: {user_data['email']}")
                    
    except Exception as e:
        print(f"Warning: Could not seed development data: {e}")


async def close_db() -> None:
    """
    Close database engine and all connections.
    
    This should be called during application shutdown.
    """
    await engine.dispose()
