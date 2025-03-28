from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero import schemas
from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.security import (
    get_current_user,
    get_password_hash,
)

router = APIRouter(prefix="/users", tags=["users"])

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
Pagination = Annotated[schemas.FilterPage, Query()]


@router.get("/", response_model=schemas.UserList)
async def read_users(session: Session, pagination: Pagination):
    query = await session.scalars(
        select(User).offset(pagination.offset).limit(pagination.limit)
    )
    users = query.all()
    return {"users": users}


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserPublic,
)
async def create_user(session: Session, user: schemas.UserSchema):
    new_user = await session.scalar(
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
    await session.commit()
    await session.refresh(new_user)

    return new_user


@router.get("/{user_id}", response_model=schemas.UserPublic)
async def read_user(session: Session, user_id: int):
    user = await session.scalar(select(User).where(User.id == user_id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=schemas.UserPublic)
async def update_user(
    session: Session,
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
        await session.commit()
        await session.refresh(current_user)

        return current_user

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    session: Session,
    current_user: CurrentUser,
    user_id: int,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to do this",
        )

    await session.delete(current_user)
    await session.commit()
