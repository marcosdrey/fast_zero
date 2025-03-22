from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from jwt import encode

ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = "my-secret-key"
ALGORITHM = "HS256"


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(tz=ZoneInfo("UTC")) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return encode(to_encode, SECRET_KEY, ALGORITHM)
