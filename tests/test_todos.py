import factory.fuzzy
import pytest
from fastapi import status

from fast_zero.models import Todo, TodoState


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker("text")
    description = factory.Faker("text")
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


def test_create_valid_todo(client, token, mock_valid_todo, mock_db_time):
    with mock_db_time(model=Todo) as time:
        response = client.post(
            "/todos",
            headers={"Authorization": f"Bearer {token}"},
            json=mock_valid_todo,
        )

        iso_time = time.isoformat()

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == dict(
            **mock_valid_todo, id=1, created_at=iso_time, updated_at=iso_time
        )


@pytest.mark.asyncio
async def test_get_todos_should_return_5_todos(session, client, user, token):
    expected_todos = 5
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        "/todos", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["todos"]) == expected_todos


@pytest.mark.asyncio
async def test_get_todos_pagination_should_return_2_todos(
    session, user, client, token
):
    expected_todos = 2
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        "/todos?offset=1&limit=2", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["todos"]) == expected_todos


@pytest.mark.asyncio
async def test_get_todos_filter_title_should_return_5_todos(
    session, user, client, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, title="TODO"),
    )
    session.add_all(TodoFactory.create_batch(5, user_id=user.id, title="any"))
    await session.commit()

    response = client.get(
        "/todos?title=todo", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["todos"]) == expected_todos


@pytest.mark.asyncio
async def test_get_todos_filter_description_should_return_5_todos(
    session, user, client, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, description="TODO"),
    )
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, description="any")
    )
    await session.commit()

    response = client.get(
        "/todos?description=todo", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["todos"]) == expected_todos


@pytest.mark.asyncio
async def test_get_todos_filter_state_should_return_5_todos(
    session, user, client, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, state=TodoState.draft),
    )
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, state=TodoState.done)
    )
    await session.commit()

    response = client.get(
        "/todos?state=done", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["todos"]) == expected_todos


@pytest.mark.asyncio
async def test_get_todos_filter_combined_should_return_5_todos(
    session, user, client, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            5,
            user_id=user.id,
            title="combined",
            description="desc combined",
            state=TodoState.doing,
        ),
    )
    session.add_all(
        TodoFactory.create_batch(
            5,
            user_id=user.id,
            title="random",
            description="desc random",
            state=TodoState.draft,
        )
    )
    await session.commit()

    response = client.get(
        "/todos?title=combined&description=desc combined&state=doing",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["todos"]) == expected_todos


@pytest.mark.asyncio
async def test_get_todos_should_return_all_expected_fields(
    session, user, client, token, mock_db_time
):
    todo = TodoFactory(user_id=user.id)
    with mock_db_time(model=Todo) as time:
        session.add(todo)
        await session.commit()

    response = client.get(
        "/todos",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["todos"] == [
        {
            "state": todo.state,
            "description": todo.description,
            "title": todo.title,
            "id": 1,
            "created_at": time.isoformat(),
            "updated_at": time.isoformat(),
        }
    ]


@pytest.mark.asyncio
async def test_patch_valid_todo(session, client, user, token):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    await session.commit()

    response = client.patch(
        f"/todos/{todo.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "patch title"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "patch title"


def test_patch_todo_that_does_not_exist_or_does_not_belong_to_current_user(
    client, token
):
    response = client.patch(
        "/todos/10", headers={"Authorization": f"Bearer {token}"}, json={}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Task not found"}


@pytest.mark.asyncio
async def test_delete_valid_todo(session, client, user, token):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    await session.commit()

    response = client.delete(
        "/todos/1", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_todo_that_does_not_exist_or_does_not_belong_to_current_user(
    client, token
):
    response = client.delete(
        "/todos/10", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Task not found"}
