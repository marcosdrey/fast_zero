from fastapi import status


def test_create_valid_user(client, mock_valid_user):
    response = client.post("/users/", json=mock_valid_user)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "username": "alice",
        "email": "alice@example.com",
        "id": 1,
    }


def test_create_user_with_username_that_already_exists(
    client, mock_valid_user
):
    client.post("/users/", json=mock_valid_user)
    same_user_response = client.post("/users/", json=mock_valid_user)

    assert same_user_response.status_code == status.HTTP_409_CONFLICT
    assert same_user_response.json() == {
        "detail": "Username already exists"
    }


def test_get_users(client):
    response = client.get("/users/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "users": [{
            "username": "alice",
            "email": "alice@example.com",
            "id": 1,
        }]
    }


def test_get_user(client):
    response = client.get("/users/1/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "username": "alice",
        "email": "alice@example.com",
        "id": 1,
    }


def test_get_user_that_does_not_exist(client):
    response = client.get("/users/0/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "User not found"
    }


def test_update_user(client, mock_valid_updated_user):
    response = client.put(
        "/users/1/",
        json=mock_valid_updated_user
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "username": mock_valid_updated_user["username"],
        "email": mock_valid_updated_user["email"],
        "id": 1,
    }


def test_update_user_that_does_not_exist(client, mock_valid_updated_user):
    response = client.put(
        "/users/0/",
        json=mock_valid_updated_user
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "User not found"
    }
