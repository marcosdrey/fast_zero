from fastapi import status


def test_root_should_return_ok_and_hello_world(client):
    response = client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Olá Mundo!"}


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
