from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.movie import Movie
from app.domain.entities.user_profile import UserProfile
from app.domain.repositories.user_profile_repository import AbstractUserProfileRepository
from app.infrastructure.database.models.movie_models import MovieModel
from app.infrastructure.database.models.users_profiles import UserProfileModel
from app.infrastructure.database.models.association_tables import user_profile_liked_movie


def _profile_to_entity(model: UserProfileModel) -> UserProfile:
    return UserProfile(
        id=model.id,
        user_id=model.user_id,
        name=model.name,
        favorite_genres=model.favorite_genres,
        about_me=model.about_me,
        image_id=model.image_id,
        created_at=model.created_at,
    )


def _movie_to_entity(model: MovieModel) -> Movie:
    return Movie(
        id=model.id, id_pois=model.id_pois, name_movie=model.name_movie,
        year=model.year, genres=model.genres, description=model.description,
        poster_image=model.poster_image, movie_length=model.movieLength,
        rating=model.rating,
    )


class UserProfileRepository(AbstractUserProfileRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: int) -> UserProfile | None:
        model = await self.session.scalar(
            select(UserProfileModel).where(UserProfileModel.user_id == user_id)
        )
        return _profile_to_entity(model) if model else None

    async def get_by_name(self, name: str) -> UserProfile | None:
        model = await self.session.scalar(
            select(UserProfileModel).where(UserProfileModel.name == name)
        )
        return _profile_to_entity(model) if model else None

    async def update(self, user_id: int, data: dict) -> UserProfile:
        await self.session.execute(
            update(UserProfileModel).where(UserProfileModel.user_id == user_id).values(**data)
        )
        model = await self.session.scalar(
            select(UserProfileModel).where(UserProfileModel.user_id == user_id)
        )
        await self.session.refresh(model)
        return _profile_to_entity(model)

    async def get_liked_movies(
        self, profile_id: int, cursor: int | None, limit: int
    ) -> tuple[list[Movie], bool]:
        query = (
            select(MovieModel)
            .join(user_profile_liked_movie, user_profile_liked_movie.c.movie_base_id == MovieModel.id)
            .where(user_profile_liked_movie.c.profile_id == profile_id)
            .order_by(MovieModel.id.desc())
        )
        if cursor:
            query = query.where(MovieModel.id < cursor)
        query = query.limit(limit + 1)

        result = await self.session.scalars(query)
        movies = result.all()
        has_more = len(movies) > limit
        items = movies[:limit]
        return [_movie_to_entity(m) for m in items], has_more

    async def is_movie_liked(self, profile_id: int, movie_id: int) -> bool:
        model = await self.session.scalar(
            select(UserProfileModel)
            .options(selectinload(UserProfileModel.liked_movie))
            .where(UserProfileModel.id == profile_id)
        )
        return any(m.id == movie_id for m in model.liked_movie)

    async def like_movie(self, profile_id: int, movie_id: int) -> None:
        profile = await self.session.scalar(
            select(UserProfileModel)
            .options(selectinload(UserProfileModel.liked_movie))
            .where(UserProfileModel.id == profile_id)
        )
        movie = await self.session.get(MovieModel, movie_id)
        profile.liked_movie.append(movie)
        await self.session.flush()

    async def unlike_movie(self, profile_id: int, movie_id: int) -> None:
        profile = await self.session.scalar(
            select(UserProfileModel)
            .options(selectinload(UserProfileModel.liked_movie))
            .where(UserProfileModel.id == profile_id)
        )
        movie = await self.session.get(MovieModel, movie_id)
        profile.liked_movie.remove(movie)
        await self.session.flush()

    async def create_empty(self, user_id: int) -> UserProfile:
        model = UserProfileModel(user_id=user_id)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return _profile_to_entity(model)