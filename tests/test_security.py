from fastapi import status
from jwt import decode

from fast_zero.security import ALGORITHM, SECRET_KEY, create_access_token


def test_access_token():
    data = {"test": "test"}
    token = create_access_token(data)

    decoded = decode(token, SECRET_KEY, algorithms=(ALGORITHM,))

    assert decoded["test"] == data["test"]
    assert "exp" in decoded


def test_invalid_token(client):
    response = client.delete(
        "/users/1", headers={"Authorization": "Bearer test"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}


def test_current_user_username_not_found(client):
    data = {"not_username": "test"}
    token = create_access_token(data)

    response = client.delete(
        "/users/1", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}


def test_current_user_not_found_in_db(client):
    data = {"sub": "inexistent"}
    token = create_access_token(data)

    response = client.delete(
        "users/1", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}
