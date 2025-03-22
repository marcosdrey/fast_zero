from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User

ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = "my-secret-key"
ALGORITHM = "HS256"

pwd_ctx = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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


def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme),
):
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode(token, SECRET_KEY, algorithms=(ALGORITHM,))
        subject_username = payload.get("sub")

        if not subject_username:
            raise credentials_exc

    except DecodeError:
        raise credentials_exc

    user = session.scalar(
        select(User).where(User.username == subject_username)
    )

    if not user:
        raise credentials_exc

    return user
