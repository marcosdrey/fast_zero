from fastapi import status


def test_get_token(client, user):
    response = client.post(
        "/auth/token",
        data={"username": user.username, "password": user.clean_password},
    )

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "token_type" in response.json()


def test_get_token_invalid_username(client, user):
    response = client.post(
        "/auth/token",
        data={"username": "wrong-username", "password": user.clean_password},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect email or password"}


def test_get_token_invalid_password(client, user):
    response = client.post(
        "/auth/token",
        data={"username": user.username, "password": "wrong-password"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect email or password"}
