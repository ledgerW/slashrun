"""Test configuration and fixtures for SlashRun API tests."""

import asyncio
import os
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

# Set required environment variables before importing app modules
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key-for-testing-only")
os.environ.setdefault("ENVIRONMENT", "test")

from main import app
from backend.app.core.database import get_db
from backend.app.core.config import settings
from db.models.user import User
from backend.app.services.auth_service import auth_service


# Test database URL - using in-memory SQLite for fast tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for the test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,
        }
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database dependency override."""
    
    async def get_test_db():
        return test_db
    
    app.dependency_overrides[get_db] = get_test_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def test_user(test_db: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=auth_service.hash_password("testpassword123"),
        full_name="Test User"
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def auth_headers(client: AsyncClient, test_user: User) -> dict:
    """Get authentication headers for test requests."""
    response = await client.post("/api/auth/login/form", data={
        "username": "test@example.com",
        "password": "testpassword123"
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 200
    token_data = response.json()
    return {"Authorization": f"Bearer {token_data['access_token']}"}


@pytest.fixture
def sample_mvs_state():
    """Sample Minimum Viable Scenario state for testing."""
    return {
        "t": 0,
        "base_ccy": "USD",
        "countries": {
            "USA": {
                "name": "USA",
                "macro": {
                    "gdp": 23000000,
                    "potential_gdp": 22800000,  # Added for output gap calculation
                    "inflation": 0.025,
                    "unemployment": 0.037,
                    "output_gap": 0.0088,  # Added: (23000000-22800000)/22800000
                    "policy_rate": 0.05,
                    "neutral_rate": 0.025,  # Added for Taylor rule
                    "debt_gdp": 0.95,
                    "primary_balance": -0.03,  # Added for debt dynamics
                    "inflation_target": 0.02
                },
                "external": {
                    "fx_rate": 1.0,
                    "reserves_usd": 150000,
                    "current_account_gdp": -0.025
                },
                "trade": {
                    "exports_gdp": 0.12,
                    "imports_gdp": 0.15,
                    "tariff_mfn_avg": 0.032
                },
                "finance": {
                    "sovereign_yield": 0.045  # Added for debt calculations
                }
            },
            "CHN": {
                "name": "CHN", 
                "macro": {
                    "gdp": 17700000,
                    "potential_gdp": 17500000,  # Added for output gap calculation
                    "inflation": 0.021,
                    "unemployment": 0.039,
                    "output_gap": 0.0114,  # Added: (17700000-17500000)/17500000
                    "policy_rate": 0.035,
                    "neutral_rate": 0.02,  # Added for Taylor rule
                    "debt_gdp": 0.67,
                    "primary_balance": -0.02,  # Added for debt dynamics
                    "inflation_target": 0.02
                },
                "external": {
                    "fx_rate": 6.8,
                    "reserves_usd": 3200000,
                    "current_account_gdp": 0.015
                },
                "trade": {
                    "exports_gdp": 0.18,
                    "imports_gdp": 0.16,
                    "tariff_mfn_avg": 0.076
                },
                "finance": {
                    "sovereign_yield": 0.032  # Added for debt calculations
                }
            }
        },
        "trade_matrix": {
            "USA": {"CHN": 120000},
            "CHN": {"USA": 450000}
        },
        "rules": {
            "regimes": {
                "monetary": {"rule": "taylor", "phi_pi": 0.5, "phi_y": 0.5},
                "fiscal": {"debt_sustainability": True},
                "fx": {"uip_rho_base": 0.0},
                "trade": {"tariff_multiplier": 1.0}
            },
            "rng_seed": 42
        }
    }


@pytest.fixture
def simple_tariff_trigger():
    """Simple tariff shock trigger for testing."""
    return {
        "name": "US-China Tariff Shock",
        "description": "Implement 25% tariffs on Chinese imports",
        "condition": {
            "when": "t >= 3",
            "once": True
        },
        "action": {
            "patches": [
                {
                    "path": "countries.USA.trade.tariff_mfn_avg",
                    "op": "set",
                    "value": 0.25
                }
            ]
        },
        "expires_after_turns": 10
    }
