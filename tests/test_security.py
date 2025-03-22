from jwt import decode

from fast_zero.security import ALGORITHM, SECRET_KEY, create_access_token


def test_access_token():
    data = {"test": "test"}
    token = create_access_token(data)

    decoded = decode(token, SECRET_KEY, algorithms=(ALGORITHM,))

    assert decoded["test"] == data["test"]
    assert "exp" in decoded
