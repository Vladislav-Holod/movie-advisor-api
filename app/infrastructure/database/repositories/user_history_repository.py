from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.movie import Movie
from app.domain.entities.user_history import UserHistory, TaskStatus
from app.domain.repositories.user_history_repository import AbstractUserHistoryRepository
from app.infrastructure.database.models.users_history import UserHistoryPrompt
from app.infrastructure.database.models.movie_models import MovieModel


def _movie_to_entity(model: MovieModel) -> Movie:
    return Movie(
        id=model.id, id_pois=model.id_pois, name_movie=model.name_movie,
        year=model.year, genres=model.genres, description=model.description,
        poster_image=model.poster_image, movie_length=model.movieLength,
        rating=model.rating,
    )


def _to_entity(model: UserHistoryPrompt) -> UserHistory:
    return UserHistory(
        id=model.id,
        task_id=model.task_id,
        prompt=model.prompt,
        response=model.response,
        status=TaskStatus(model.status.value),
        user_id=model.user_id,
        created_at=model.created_at,
        movie_recommend=[_movie_to_entity(m) for m in model.movie_recommend],
    )


class UserHistoryRepository(AbstractUserHistoryRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, history: UserHistory) -> UserHistory:
        model = UserHistoryPrompt(
            task_id=history.task_id,
            prompt=history.prompt,
            response=history.response,
            status=history.status.value,
            user_id=history.user_id,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return _to_entity(model)

    async def get_by_task_id(self, task_id: str, user_id: int) -> UserHistory | None:
        model = await self.session.scalar(
            select(UserHistoryPrompt)
            .options(selectinload(UserHistoryPrompt.movie_recommend))
            .where(
                UserHistoryPrompt.task_id == task_id,
                UserHistoryPrompt.user_id == user_id,
            )
        )
        return _to_entity(model) if model else None

    async def get_by_id(self, history_id: int, user_id: int) -> UserHistory | None:
        model = await self.session.scalar(
            select(UserHistoryPrompt).where(
                UserHistoryPrompt.user_id == user_id,
                UserHistoryPrompt.id == history_id,
            )
        )
        return _to_entity(model) if model else None

    async def list_with_recommendations(
        self, user_id: int, cursor: int | None, limit: int
    ) -> tuple[list[UserHistory], bool]:
        query = (
            select(UserHistoryPrompt)
            .options(selectinload(UserHistoryPrompt.movie_recommend))
            .where(
                UserHistoryPrompt.user_id == user_id,
                UserHistoryPrompt.movie_recommend != None,
            )
            .order_by(UserHistoryPrompt.created_at.desc())
        )
        if cursor:
            query = query.where(UserHistoryPrompt.id < cursor)
        query = query.limit(limit + 1)

        result = await self.session.scalars(query)
        items = result.all()
        has_more = len(items) > limit
        page = items[:limit]
        return [_to_entity(m) for m in page], has_more

    async def set_status(self, task_id: str, status: TaskStatus) -> None:
        history = await self.session.scalar(
            select(UserHistoryPrompt).where(UserHistoryPrompt.task_id == task_id)
        )
        if history is None:
            raise ValueError(f"No UserHistoryPrompt with task_id: {task_id}")
        history.status = status
        await self.session.flush()

    async def complete(self, task_id: str, response: str, movie_ids: list[int]) -> None:
        history = await self.session.scalar(
            select(UserHistoryPrompt)
            .options(selectinload(UserHistoryPrompt.movie_recommend))
            .where(UserHistoryPrompt.task_id == task_id)
        )
        if history is None:
            raise ValueError(f"No UserHistoryPrompt with task_id: {task_id}")

        movies = (
            await self.session.scalars(
                select(MovieModel).where(MovieModel.id_pois.in_(movie_ids))
            )
        ).all()
        history.movie_recommend = movies
        history.response = response
        history.status = TaskStatus.SUCCESS
        await self.session.flush()