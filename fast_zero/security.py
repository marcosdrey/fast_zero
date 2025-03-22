from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from jwt import encode
from pwdlib import PasswordHash

ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = "my-secret-key"
ALGORITHM = "HS256"
pwd_ctx = PasswordHash.recommended()


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(tz=ZoneInfo("UTC")) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return encode(to_encode, SECRET_KEY, ALGORITHM)


def get_password_hash(password: str):
    return pwd_ctx.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_ctx.verify(plain_password, hashed_password)
