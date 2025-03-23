from pydantic import BaseModel, ConfigDict, EmailStr


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserList(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    token_type: str
    access_token: str


class FilterPage(BaseModel):
    offset: int = 0
    limit: int = 100
