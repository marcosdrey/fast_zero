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
