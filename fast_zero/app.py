from fastapi import FastAPI, HTTPException, status

from fast_zero import schemas

app = FastAPI()

database: list[schemas.UserDB] = []


@app.get("/")
def read_root():
    return {"message": "Olá Mundo!"}


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
