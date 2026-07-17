from app.domain.entities.movie import Movie
from app.domain.repositories.movie_repository import AbstractMovieRepository
from app.domain.repositories.user_profile_repository import AbstractUserProfileRepository


class ProfileNotFoundError(Exception):
    pass


class MovieNotFoundError(Exception):
    pass


class AlreadyLikedError(Exception):
    pass


class NotLikedError(Exception):
    pass


class LikeMovieUseCase:
    def __init__(
        self,
        profile_repo: AbstractUserProfileRepository,
        movie_repo: AbstractMovieRepository,
    ):
        self.profile_repo = profile_repo
        self.movie_repo = movie_repo

    async def execute(self, user_id: int, movie_id: int) -> Movie:
        profile = await self.profile_repo.get_by_user_id(user_id)
        if profile is None or profile.name is None:
            raise ProfileNotFoundError()

        movie = await self.movie_repo.get_by_id(movie_id)
        if movie is None:
            raise MovieNotFoundError()

        if await self.profile_repo.is_movie_liked(profile.id, movie_id):
            raise AlreadyLikedError()

        await self.profile_repo.like_movie(profile.id, movie_id)
        return movie


class UnlikeMovieUseCase:
    def __init__(
        self,
        profile_repo: AbstractUserProfileRepository,
        movie_repo: AbstractMovieRepository,
    ):
        self.profile_repo = profile_repo
        self.movie_repo = movie_repo

    async def execute(self, user_id: int, movie_id: int) -> None:
        profile = await self.profile_repo.get_by_user_id(user_id)
        if profile is None:
            raise ProfileNotFoundError()

        movie = await self.movie_repo.get_by_id(movie_id)
        if movie is None:
            raise MovieNotFoundError()

        if not await self.profile_repo.is_movie_liked(profile.id, movie_id):
            raise NotLikedError()

        await self.profile_repo.unlike_movie(profile.id, movie_id)


class GetLikedMoviesUseCase:
    def __init__(self, profile_repo: AbstractUserProfileRepository):
        self.profile_repo = profile_repo

    async def execute(
        self, user_id: int, cursor: int | None, limit: int
    ) -> tuple[list[Movie], int | None, bool]:
        profile = await self.profile_repo.get_by_user_id(user_id)
        if profile is None:
            raise ProfileNotFoundError()

        movies, has_more = await self.profile_repo.get_liked_movies(profile.id, cursor, limit)
        next_cursor = movies[-1].id if has_more and movies else None
        return movies, next_cursor, has_more