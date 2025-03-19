import pytest
from fastapi.testclient import TestClient

from fast_zero.app import app


@pytest.fixture
def client():
    return TestClient(app)


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
        "password": "editedsecretpassword"
    }
