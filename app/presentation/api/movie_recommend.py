from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.user_history import CreateHistoryUseCase
from app.infrastructure.database.repositories.user_history_repository import UserHistoryRepository
from app.infrastructure.database.session import get_async_db
from app.infrastructure.tasks.movie_task import recommend_movie_task
from app.presentation.dependencies import get_current_user
from app.presentation.schemas.movie_schemas import MoviePrompt

router = APIRouter(prefix='/movie', tags=['AI'])


def get_create_history_use_case(db: AsyncSession = Depends(get_async_db)) -> CreateHistoryUseCase:
    return CreateHistoryUseCase(UserHistoryRepository(db))


@router.post('/recommend')
async def recommend_movie_endpoint(
    prompt: MoviePrompt,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_user),
    use_case: CreateHistoryUseCase = Depends(get_create_history_use_case),
):
    history = await use_case.execute(current_user.id, prompt.prompt)
    await db.commit()

    recommend_movie_task.delay(history.task_id, prompt.prompt)

    return {'task_id': history.task_id}