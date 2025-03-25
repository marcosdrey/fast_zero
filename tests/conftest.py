from contextlib import contextmanager
from datetime import datetime

import factory
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry
from fast_zero.security import get_password_hash


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda x: f"test_{x}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@test.com")
    password = factory.LazyAttribute(lambda obj: f"{obj.username}-secret")


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user(session):
    pwd = "test123"

    user = UserFactory(password=get_password_hash(pwd))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = pwd

    return user


@pytest_asyncio.fixture
async def other_user(session):
    pwd = "test123"

    user = UserFactory(password=get_password_hash(pwd))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = pwd

    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        "/auth/token",
        data={"username": user.username, "password": user.clean_password},
    )
    return response.json()["access_token"]


@pytest.fixture
def mock_valid_user():
    return {
        "username": "alice",
        "email": "alice@example.com",
        "password": "supersecretpassword",
    }


@pytest.fixture
def mock_valid_updated_user():
    return {
        "username": "edited_user",
        "email": "edited_user@example.com",
        "password": "editedsecretpassword",
    }


@pytest.fixture
def mock_valid_todo():
    return {
        "title": "test todo",
        "description": "test description",
        "state": "draft",
    }


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@contextmanager
def _mock_db_time(*, model, time=datetime(2025, 1, 1)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, "created_at"):
            target.created_at = time
        if hasattr(target, "updated_at"):
            target.updated_at = time

    event.listen(model, "before_insert", fake_time_hook)

    yield time

    event.remove(model, "before_insert", fake_time_hook)
