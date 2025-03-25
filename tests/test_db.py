from dataclasses import asdict

import pytest
from sqlalchemy import select

from fast_zero.models import User


@pytest.mark.asyncio
async def test_db_create_user(session, mock_valid_user, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(**mock_valid_user)
        session.add(new_user)
        await session.commit()

    user = await session.scalar(
        select(User).where(User.username == mock_valid_user["username"])
    )

    mock_valid_user.update({
        "id": 1,
        "created_at": time,
        "updated_at": time,
        "todos": []
    })

    assert asdict(user) == mock_valid_user
