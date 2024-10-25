"""
Configuration for testing API.
"""

import os
import pytest
import contextlib
import uuid

from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from datetime import date

from fastapi_users.password import PasswordHelper
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher


os.environ["ENV_STATE"] = "testing"  # noqa E402
from pickemApi.main import app
from pickemApi.database import engine, get_db
from pickemApi.models.model import Base, User, Tournament, Event, QuestionType
from pickemApi.models.usermanager import get_user_manager


password_hash = PasswordHash((Argon2Hasher(),))
password_helper = PasswordHelper(password_hash)

get_async_session_context = contextlib.asynccontextmanager(get_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


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
    async with get_async_session_context() as session:
        yield session


@pytest.fixture
async def user_manager(db_session) -> AsyncGenerator:
    """Fixture for UserManager to be used in tests."""
    async with get_user_manager_context() as user_manager:
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
    client.user_id = registered_user.id
    return client


@pytest.fixture
async def superuser(db_session) -> User:
    """Create a superuser for testing."""
    plain_password = "Test123"
    hashed_password = password_helper.hash(plain_password)

    superuser_data = {
        "email": "superuser@example.com",
        "hashed_password": hashed_password,
        "username": "Super_User",
        "is_superuser": True,
    }

    # Stwórz nowego użytkownika
    superuser = User(**superuser_data)
    db_session.add(superuser)
    await db_session.commit()

    return superuser


@pytest.fixture
async def authorized_superclient(
    async_client: AsyncClient, superuser: User
) -> AsyncClient:
    """Return logged in superuser."""
    user_data = {"username": superuser.email, "password": "Test123"}

    res = await async_client.post("/auth/jwt/login", data=user_data)

    res.raise_for_status()

    token = res.json()["access_token"]

    client = async_client
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.fixture
async def created_tournament(db_session):
    new_tournament = Tournament(name="Puchar Świata", date=date(2024, 10, 24))
    db_session.add(new_tournament)
    await db_session.commit()
    await db_session.refresh(new_tournament)
    return new_tournament


@pytest.fixture
async def created_event(
    created_tournament: Tournament,
    db_session,
    question_type: QuestionType = QuestionType.SINGLE_CHOICE,
    question_text: str = "Kto wygra mecz?",
    points_value: int = 10,
) -> Event:
    event_data = {
        "id": uuid.uuid4(),
        "tournament_id": created_tournament.id,
        "question_type": question_type,
        "question_text": question_text,
        "points_value": points_value,
    }

    event = Event(**event_data)

    db_session.add(event)
    await db_session.commit()
    await db_session.refresh(event)

    return event


@pytest.fixture
async def create_event(
    created_tournament: Tournament,
    db_session,
    question_type: QuestionType = QuestionType.SINGLE_CHOICE,
    question_text: str = "Kto wygra mecz?",
    points_value: int = 10,
) -> Event:
    event_data = {
        "id": uuid.uuid4(),
        "tournament_id": created_tournament.id,
        "question_type": question_type,
        "question_text": question_text,
        "points_value": points_value,
    }

    event = Event(**event_data)

    db_session.add(event)
    await db_session.commit()
    await db_session.refresh(event)

    return event
