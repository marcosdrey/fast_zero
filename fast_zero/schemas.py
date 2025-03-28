from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from fast_zero.models import TodoState


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


class TodoSchema(BaseModel):
    title: str
    description: str
    state: TodoState


class TodoPublic(TodoSchema):
    id: int
    created_at: datetime
    updated_at: datetime


class TodoList(BaseModel):
    todos: list[TodoPublic]


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    state: str | None = None


class FilterTodo(FilterPage):
    title: str | None = None
    description: str | None = None
    state: TodoState | None = None
