"""
Configuration for testing API.
"""

import os
import pytest

from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport


os.environ["ENV_STATE"] = "testing"  # noqa E402
from pickemApi.main import app
from pickemApi.database import engine, get_db
from pickemApi.config import config
from pickemApi.models.model import Base, User
from pickemApi.models.usermanager import get_user_manager


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
async def db_setup():
    """Create and drop the database tables for testing."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Tworzenie tabel
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Usuwanie tabel


@pytest.fixture
async def async_client(db_setup) -> AsyncGenerator:
    """Asynchronous HTTP client for testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def db_session(db_setup) -> AsyncGenerator:
    """Temporary in-memory database session for testing."""
    async for session in get_db():
        yield session


@pytest.fixture
async def user_manager(db_session) -> AsyncGenerator:
    """Fixture for UserManager to be used in tests."""
    async for user_manager in get_user_manager():
        yield user_manager


@pytest.fixture
async def registered_user(async_client: AsyncClient) -> User:
    """Return registered user."""
    user_data = {
        "email": "testuser@example.com",
        "password": "strongpassword",
        "username": "Test_User",
    }
    res = await async_client.post("/auth/register", json=user_data)

    res.raise_for_status()

    registered_user_data = res.json()
    registered_user = User(**registered_user_data)
    return registered_user


@pytest.fixture
async def authorized_client(
    async_client: AsyncClient, registered_user: User
) -> AsyncClient:
    """Return logged in user."""
    user_data = {"username": registered_user.email, "password": "strongpassword"}

    res = await async_client.post("/auth/jwt/login", data=user_data)

    res.raise_for_status()

    token = res.json()["access_token"]

    client = async_client
    client.headers["Authorization"] = f"Bearer {token}"
    return client
