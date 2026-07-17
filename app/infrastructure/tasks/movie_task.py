import asyncio
from app.domain.entities.user_history import TaskStatus
from app.application.use_cases.recommend_movie import MarkTaskRunningUseCase, RecommendMovieUseCase
from app.infrastructure.database.repositories.movie_repository import MovieRepository
from app.infrastructure.database.repositories.user_history_repository import UserHistoryRepository
from app.infrastructure.database.session import async_session_maker
from app.infrastructure.tasks.celery_app import celery_app
from app.infrastructure.tasks.container import ai_recommendation_service, poiskino_provider


@celery_app.task(bind=True, max_retries=3, retry_backoff=True)
def recommend_movie_task(self, task_id: str, prompt_text: str):
    asyncio.run(_run(task_id, prompt_text))


async def _run(task_id: str, prompt_text: str):
    async with async_session_maker() as db:
        history_repo = UserHistoryRepository(db)
        movie_repo = MovieRepository(db)

        await MarkTaskRunningUseCase(history_repo).execute(task_id)
        await db.commit()

        use_case = RecommendMovieUseCase(
            history_repo=history_repo,
            movie_repo=movie_repo,
            search_provider=poiskino_provider,
            ai_service=ai_recommendation_service,
        )
        try:
            await use_case.execute(task_id, prompt_text)
            await db.commit()
        except Exception:
            await db.rollback()
            await history_repo.set_status(task_id, TaskStatus.FAILED)
            await db.commit()
            raise