"""Integration test configuration for SlashRun API tests running against Docker Compose."""

import asyncio
import os
import pytest
import pytest_asyncio
import psycopg
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel, text

# Import app modules after setting environment
from backend.app.core.config import settings
from db.models.user import User
from backend.app.services.auth_service import auth_service


# Integration test database URL - connects to same database as running Docker backend
INTEGRATION_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/slashrun"
INTEGRATION_API_BASE_URL = "http://localhost:8000"


def check_docker_compose_running():
    """Check if Docker Compose services are running."""
    import subprocess
    import json
    try:
        # Use modern docker compose syntax and JSON format
        result = subprocess.run([
            "docker", "compose", "ps", "--format", "json"
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode != 0:
            pytest.skip("Docker Compose is not running. Run 'docker compose up -d' first.")
        
        if not result.stdout.strip():
            pytest.skip("No Docker Compose containers found.")
            
        # Parse JSON output to check for running services
        containers = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                try:
                    containers.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        running_services = [c['Service'] for c in containers if c.get('State') == 'running']
        health_status = {c['Service']: c.get('Health', 'unknown') for c in containers}
        
        if 'db' not in running_services:
            pytest.skip("PostgreSQL service (db) is not running in Docker Compose.")
            
        if 'backend' not in running_services:
            pytest.skip("Backend service is not running in Docker Compose.")
            
        # Check health status if available
        if health_status.get('db') not in ['healthy', 'unknown']:
            pytest.skip(f"PostgreSQL service is unhealthy: {health_status.get('db')}")
            
        if health_status.get('backend') not in ['healthy', 'unknown']:
            pytest.skip(f"Backend service is unhealthy: {health_status.get('backend')}")
            
        # Test PostgreSQL connection
        import psycopg
        conn = psycopg.connect(
            host="localhost", 
            port=5432, 
            dbname="slashrun", 
            user="postgres", 
            password="postgres",
            connect_timeout=10
        )
        conn.close()
        
        # Test API server
        import requests
        response = requests.get(f"{INTEGRATION_API_BASE_URL}/health", timeout=10)
        if response.status_code != 200:
            pytest.skip(f"API server is not responding at {INTEGRATION_API_BASE_URL}")
            
    except Exception as e:
        pytest.skip(f"Docker Compose services not available: {e}")


@pytest.fixture(scope="session", autouse=True)
def check_docker_services():
    """Automatically check Docker services before running integration tests."""
    check_docker_compose_running()


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for the test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def integration_engine():
    """Create integration test database engine connected to running Docker backend database."""
    # Connect directly to the same database the backend is using
    engine = create_async_engine(
        INTEGRATION_DATABASE_URL,
        echo=False
    )
    
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def integration_db(integration_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create integration test database session - work with running backend database."""
    async_session = async_sessionmaker(
        integration_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        # Note: We don't rollback here since we're working with the live backend
        # Test cleanup should be handled via API calls or specific cleanup methods


@pytest_asyncio.fixture(scope="function")
async def integration_client() -> AsyncGenerator[AsyncClient, None]:
    """Create HTTP client for integration tests against running Docker Compose API."""
    async with AsyncClient(
        base_url=INTEGRATION_API_BASE_URL,
        timeout=30.0  # Longer timeout for integration tests
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def integration_test_user(integration_db: AsyncSession) -> User:
    """Create a test user in the integration database."""
    user = User(
        email="integration_test@example.com",
        username="integration_testuser",
        hashed_password=auth_service.hash_password("integration_testpass123"),
        full_name="Integration Test User"
    )
    integration_db.add(user)
    await integration_db.commit()
    await integration_db.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def integration_auth_headers(integration_client: AsyncClient) -> dict:
    """Get authentication headers for integration test requests."""
    
    # First try to login with default admin user (should exist from database init)
    admin_login_data = {
        "username": "admin@slashrun.com",  # Default admin email from config
        "password": "admin123"            # Default admin password from config
    }
    
    login_response = await integration_client.post("/api/auth/login/form", data=admin_login_data, 
                                                  headers={"Content-Type": "application/x-www-form-urlencoded"})
    
    if login_response.status_code == 200:
        # Admin user login successful
        token_data = login_response.json()
        return {"Authorization": f"Bearer {token_data['access_token']}"}
    
    # If admin login fails, try to create a test user
    user_data = {
        "email": "integration_auth@example.com",
        "password": "integration_authpass123",
        "username": "integration_authuser",
        "full_name": "Integration Auth User"
    }
    
    # Register user (ignore if already exists)
    register_response = await integration_client.post("/api/users/register", json=user_data)
    
    # Now try to login with test user
    test_login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    
    login_response = await integration_client.post("/api/auth/login/form", data=test_login_data,
                                                  headers={"Content-Type": "application/x-www-form-urlencoded"})
    
    if login_response.status_code != 200:
        # Get detailed error information
        try:
            error_text = login_response.text
        except:
            error_text = str(login_response.content) if hasattr(login_response, 'content') else "Unknown error"
        raise AssertionError(f"Login failed for both admin and test user. Status: {login_response.status_code}, Response: {error_text}")
    
    token_data = login_response.json()
    return {"Authorization": f"Bearer {token_data['access_token']}"}


@pytest.fixture
def sample_integration_mvs_state():
    """Sample MVS state for integration testing."""
    return {
        "t": 0,
        "base_ccy": "USD",
        "countries": {
            "USA": {
                "name": "USA",
                "macro": {
                    "gdp": 23000000,
                    "potential_gdp": 22800000,
                    "inflation": 0.025,
                    "unemployment": 0.037,
                    "output_gap": 0.0088,
                    "policy_rate": 0.05,
                    "neutral_rate": 0.025,
                    "debt_gdp": 0.95,
                    "primary_balance": -0.03,
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
                    "sovereign_yield": 0.045
                }
            },
            "CHN": {
                "name": "CHN", 
                "macro": {
                    "gdp": 17700000,
                    "potential_gdp": 17500000,
                    "inflation": 0.021,
                    "unemployment": 0.039,
                    "output_gap": 0.0114,
                    "policy_rate": 0.035,
                    "neutral_rate": 0.02,
                    "debt_gdp": 0.67,
                    "primary_balance": -0.02,
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
                    "sovereign_yield": 0.032
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


# Utility functions for integration tests
async def cleanup_integration_test_data(integration_db: AsyncSession):
    """Clean up test data from integration database."""
    # Clean up scenarios, states, audits, triggers for test users
    await integration_db.execute(
        text("DELETE FROM scenarios WHERE owner_id IN (SELECT id FROM users WHERE email LIKE '%integration_%' OR email LIKE '%test_%')")
    )
    await integration_db.execute(
        text("DELETE FROM users WHERE email LIKE '%integration_%' OR email LIKE '%test_%'")
    )
    await integration_db.commit()


def requires_docker_compose(f):
    """Decorator to skip tests if Docker Compose is not running."""
    # Since we already have a session-level autouse fixture (check_docker_services)
    # that calls check_docker_compose_running(), this decorator just returns
    # the function unchanged to preserve fixture injection
    return f
