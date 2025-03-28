from fastapi import status

from fast_zero.schemas import UserPublic


def test_create_user(client, mock_valid_user):
    response = client.post("/users/", json=mock_valid_user)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "username": mock_valid_user["username"],
        "email": mock_valid_user["email"],
        "id": 1,
    }


def test_create_user_with_username_that_already_exists(
    client, mock_valid_user
):
    client.post("/users/", json=mock_valid_user)
    same_user_response = client.post("/users/", json=mock_valid_user)

    assert same_user_response.status_code == status.HTTP_409_CONFLICT
    assert same_user_response.json() == {"detail": "Username already exists"}


def test_create_user_with_email_that_already_exists(client, mock_valid_user):
    client.post("/users/", json=mock_valid_user)

    mock_valid_user["username"] = "any"

    same_user_response = client.post("/users/", json=mock_valid_user)

    assert same_user_response.status_code == status.HTTP_409_CONFLICT
    assert same_user_response.json() == {"detail": "Email already exists"}


def test_read_users_with_empty_db(client):
    response = client.get("/users/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"users": []}


def test_read_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get("/users/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"users": [user_schema]}


def test_read_user(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get("/users/1/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == user_schema


def test_read_user_that_does_not_exist(client):
    response = client.get("/users/0/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "User not found"}


def test_update_user(client, user, mock_valid_updated_user, token):
    response = client.put(
        f"/users/{user.id}/",
        headers={"Authorization": f"Bearer {token}"},
        json=mock_valid_updated_user,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "username": mock_valid_updated_user["username"],
        "email": mock_valid_updated_user["email"],
        "id": user.id,
    }


def test_update_user_without_permission(
    client, token, other_user, mock_valid_updated_user
):
    response = client.put(
        f"/users/{other_user.id}/",
        headers={"Authorization": f"Bearer {token}"},
        json=mock_valid_updated_user,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": "You don't have permission to do this"
    }


def test_update_user_violates_unique_constraint(
    client, user, other_user, token
):
    response = client.put(
        f"/users/{user.id}/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": other_user.username,
            "email": other_user.email,
            "password": other_user.password,
        },
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": "Username or email already exists"}


def test_delete_user(client, token):
    response = client.delete(
        "/users/1/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_user_without_permission(client, token, other_user):
    response = client.delete(
        f"/users/{other_user.id}/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": "You don't have permission to do this"
    }
