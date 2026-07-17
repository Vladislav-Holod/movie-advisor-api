from abc import ABC, abstractmethod

from app.domain.entities.movie import Movie


class AbstractMovieRepository(ABC):
    @abstractmethod
    async def get_by_id(self, movie_id: int) -> Movie | None: ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Movie | None: ...

    @abstractmethod
    async def list_all(self) -> list[Movie]: ...

    @abstractmethod
    async def create(self, movie: Movie) -> Movie: ...