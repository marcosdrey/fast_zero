from dataclasses import asdict

import pytest
from sqlalchemy import select

from fast_zero.models import Todo, User


@pytest.mark.asyncio
async def test_db_create_user(session, mock_valid_user, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(**mock_valid_user)
        session.add(new_user)
        await session.commit()

    user = await session.scalar(
        select(User).where(User.username == mock_valid_user["username"])
    )

    mock_valid_user.update(
        {"id": 1, "created_at": time, "updated_at": time, "todos": []}
    )

    assert asdict(user) == mock_valid_user


@pytest.mark.asyncio
async def test_db_create_todo(session, user, mock_db_time):
    todo_dict = {
        "title": "Test Todo",
        "description": "Test Desc",
        "state": "draft",
        "user_id": user.id,
    }

    with mock_db_time(model=Todo) as time:
        todo = Todo(**todo_dict)
        session.add(todo)
        await session.commit()

    todo = await session.scalar(select(Todo))

    assert asdict(todo) == dict(
        **todo_dict, id=1, created_at=time, updated_at=time
    )


@pytest.mark.asyncio
async def test_db_user_todo_relationship(session, user):
    todo_dict = {
        "title": "Test Todo",
        "description": "Test Desc",
        "state": "draft",
        "user_id": user.id,
    }

    todo = Todo(**todo_dict)

    session.add(todo)
    await session.commit()
    await session.refresh(user)

    user = await session.scalar(select(User).where(User.id == user.id))

    assert user.todos == [todo]


@pytest.mark.asyncio
async def test_create_todo_with_invalid_state(session, user):
    todo = Todo(
        title='todo title',
        description='todo desc',
        state='test',
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()

    with pytest.raises(LookupError):
        await session.scalar(select(Todo))
