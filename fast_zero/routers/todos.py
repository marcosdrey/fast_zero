from typing import Annotated

from fastapi import APIRouter, Depends, status
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
