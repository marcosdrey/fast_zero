from fastapi import FastAPI, HTTPException, status

from fast_zero import schemas

app = FastAPI()

database: list[schemas.UserDB] = []


@app.get("/users/", response_model=schemas.UserList)
def get_users():
    return {"users": database}


@app.post(
    "/users/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserPublic,
)
def create_user(user: schemas.UserSchema):
    new_user = schemas.UserDB(**user.model_dump(), id=len(database) + 1)

    if any(
        user_db.model_dump()["username"] == new_user.username
        for user_db in database
    ):
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail="Username already exists"
        )

    database.append(new_user)
    return new_user


@app.get("/users/{user_id}/", response_model=schemas.UserPublic)
def get_user(user_id: int):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return database[user_id - 1]


@app.put("/users/{user_id}/", response_model=schemas.UserPublic)
def update_user(user_id: int, user: schemas.UserSchema):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    user_with_id = schemas.UserDB(**user.model_dump(), id=user_id)
    database[user_id - 1] = user_with_id

    return user_with_id


@app.delete("/users/{user_id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    del database[user_id - 1]
