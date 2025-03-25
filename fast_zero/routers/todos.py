from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero import schemas
from fast_zero.database import get_session
from fast_zero.models import Todo, User
from fast_zero.security import get_current_user

router = APIRouter(prefix="/todos", tags=["todos"])

CurrentUser = Annotated[User, Depends(get_current_user)]
Session = Annotated[AsyncSession, Depends(get_session)]


@router.post(
    "/", response_model=schemas.TodoPublic, status_code=status.HTTP_201_CREATED
)
async def create_todo(
    session: Session, user: CurrentUser, todo: schemas.TodoSchema
):
    db_todo = Todo(**todo.model_dump(), user_id=user.id)
    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.get("/", response_model=schemas.TodoList)
async def get_todos(
    session: Session,
    user: CurrentUser,
    todo_filter: Annotated[schemas.FilterTodo, Query()],
):
    query = select(Todo).where(Todo.user_id == user.id)

    if todo_filter.title:
        query = query.where(Todo.title.icontains(todo_filter.title))

    if todo_filter.description:
        query = query.where(
            Todo.description.icontains(todo_filter.description)
        )

    if todo_filter.state:
        query = query.where(Todo.state == todo_filter.state)

    query = query.offset(todo_filter.offset).limit(todo_filter.limit)

    todos = await session.scalars(query)

    return {"todos": todos.all()}


@router.patch("/{todo_id}", response_model=schemas.TodoPublic)
async def partial_update_todo(
    todo_id: int,
    session: Session,
    user: CurrentUser,
    todo: schemas.TodoUpdate
):
    db_todo = await session.scalar(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id)
    )
    if not db_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo
