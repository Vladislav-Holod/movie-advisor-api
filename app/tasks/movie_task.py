import asyncio
from sqlalchemy import select

from app.dependencies import celery_app
from app.database import async_session_maker
from app.models.users_history import UserHistoryPrompt, TaskStatus
from app.dependencies import ai_client, api_kinopoisk
from app.services.movie_recommend_sevice import recommend_movie


@celery_app.task(bind=True, max_retries=3, retry_backoff=True)
def recommend_movie_task(self,task_id: str, prompt_text: str):
    asyncio.run(_run(task_id, prompt_text))


async def _run(task_id: str, prompt_text: str):
    async with async_session_maker() as db:
        try:
            await recommend_movie(
                prompt_text=prompt_text,
                db=db,
                task_id=task_id,
                ai_client=ai_client,
                api_kinopoisk=api_kinopoisk,
            )
        except Exception as e:
            await db.rollback()
            history_response = await db.scalar(
                select(UserHistoryPrompt).where(UserHistoryPrompt.task_id == task_id)
            )
            if history_response:
                history_response.status = TaskStatus.FAILED
                await db.commit()
            
            raise