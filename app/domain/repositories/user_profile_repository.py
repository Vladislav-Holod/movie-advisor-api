from abc import ABC, abstractmethod

from app.domain.entities.movie import Movie
from app.domain.entities.user_profile import UserProfile


class AbstractUserProfileRepository(ABC):
    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> UserProfile | None: ...

    @abstractmethod
    async def get_by_name(self, name: str) -> UserProfile | None: ...

    @abstractmethod
    async def update(self, user_id: int, data: dict) -> UserProfile: ...

    @abstractmethod
    async def get_liked_movies(
        self, profile_id: int, cursor: int | None, limit: int
    ) -> tuple[list[Movie], bool]: ...
    """Возвращает (movies, has_more)."""

    @abstractmethod
    async def is_movie_liked(self, profile_id: int, movie_id: int) -> bool: ...

    @abstractmethod
    async def like_movie(self, profile_id: int, movie_id: int) -> None: ...

    @abstractmethod
    async def unlike_movie(self, profile_id: int, movie_id: int) -> None: ...