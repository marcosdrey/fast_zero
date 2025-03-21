from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_zero import schemas
from fast_zero.database import get_session
from fast_zero.models import User

app = FastAPI()


@app.get("/users/", response_model=schemas.UserList)
def read_users(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    users = session.scalars(select(User).offset(skip).limit(limit)).all()
    return {"users": users}


@app.post(
    "/users/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserPublic,
)
def create_user(
    user: schemas.UserSchema, session: Session = Depends(get_session)
):
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

    new_user = User(**user.model_dump())
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user


@app.get("/users/{user_id}/", response_model=schemas.UserPublic)
def read_user(user_id: int, session: Session = Depends(get_session)):
    user = session.scalar(select(User).where(User.id == user_id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@app.put("/users/{user_id}/", response_model=schemas.UserPublic)
def update_user(
    user_id: int,
    user: schemas.UserSchema,
    session: Session = Depends(get_session),
):
    db_user = session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    try:
        db_user.username = user.username
        db_user.email = user.email
        db_user.password = user.password
        session.commit()
        session.refresh(db_user)

        return db_user

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        )


@app.delete("/users/{user_id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    db_user = session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    session.delete(db_user)
    session.commit()
