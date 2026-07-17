from abc import ABC, abstractmethod

from app.domain.entities.movie import Movie


class AbstractMovieSearchProvider(ABC):
    @abstractmethod
    async def search_by_filters(self, filters: dict, limit: int = 15) -> list[Movie]: ...


class MovieSearchProviderError(Exception):
    pass