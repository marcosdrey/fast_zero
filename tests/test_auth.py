from fastapi import status
from freezegun import freeze_time


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


def test_token_expired_after_time(client, user):
    with freeze_time("2025-01-01 10:00:00"):
        response = client.post(
            "/auth/token",
            data={"username": user.username, "password": user.clean_password},
        )
        assert response.status_code == status.HTTP_200_OK
        token = response.json()["access_token"]

    with freeze_time("2025-01-01 10:31:00"):
        response = client.delete(
            f"/users/{user.id}", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Could not validate credentials"}


def test_refresh_token(client, token):
    response = client.post(
        "/auth/refresh", headers={"Authorization": f"Bearer {token}"}
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
