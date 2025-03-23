from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_zero import schemas
from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.security import (
    get_current_user,
    get_password_hash,
)

router = APIRouter(prefix="/users", tags=["users"])

T_Session = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("/", response_model=schemas.UserList)
def read_users(session: T_Session, skip: int = 0, limit: int = 100):
    users = session.scalars(select(User).offset(skip).limit(limit)).all()
    return {"users": users}


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserPublic,
)
def create_user(session: T_Session, user: schemas.UserSchema):
    new_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if new_user:
        if new_user.username == user.username:
            raise HTTPException(
                status.HTTP_409_CONFLICT, detail="Username already exists"
            )
        elif new_user.email == user.email:
            raise HTTPException(
                status.HTTP_409_CONFLICT, detail="Email already exists"
            )

    hashed_password = get_password_hash(user.password)

    new_user = User(
        username=user.username, email=user.email, password=hashed_password
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user


@router.get("/{user_id}", response_model=schemas.UserPublic)
def read_user(session: T_Session, user_id: int):
    user = session.scalar(select(User).where(User.id == user_id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=schemas.UserPublic)
def update_user(
    session: T_Session,
    current_user: CurrentUser,
    user_id: int,
    user: schemas.UserSchema,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to do this",
        )
    try:
        current_user.username = user.username
        current_user.email = user.email
        current_user.password = get_password_hash(user.password)
        session.commit()
        session.refresh(current_user)

        return current_user

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    session: T_Session,
    current_user: CurrentUser,
    user_id: int,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to do this",
        )

    session.delete(current_user)
    session.commit()
