from aiohttp import ClientSession
from loguru import logger

from app.domain.entities.movie import Movie
from app.domain.repositories.movie_search_provider import (
    AbstractMovieSearchProvider,
    MovieSearchProviderError,
)

_default_movie_poster = 'https://img.magnific.com/premium-vector/black-blank-book-cover-isolated-transparent_168129-46.jpg?semt=ais_hybrid&w=740'


def _to_entity(raw: dict) -> Movie:
    return Movie(
        id=None,
        id_pois=raw.get('id'),
        name_movie=raw.get('alternativeName') or raw.get('name') or 'Без имени',
        genres=[g['name'] for g in (raw.get('genres') or [])],
        year=raw.get('year'),
        description=raw.get('description'),
        poster_image=(raw.get('poster') or {}).get('previewUrl') or _default_movie_poster,
        movie_length=raw.get('movieLength'),
        rating=(raw.get('rating') or {}).get('kp') or 0.0,
    )


class PoiskinoProvider(AbstractMovieSearchProvider):
    def __init__(self, api_key: str):
        self.__api_key = api_key

    async def search_by_filters(self, filters: dict, limit: int = 15) -> list[Movie]:
        params = {
            'limit': limit,
            'sortField': filters.get('sortField', 'rating.kp'),
            'sortType': filters.get('sortType', '-1'),
            'type': filters.get('type', 'movie'),
            'status': 'completed',
            'notNullFields': 'name',
        }
        if 'genres' in filters:
            params['genres.name'] = filters['genres']
        if 'year' in filters:
            params['year'] = filters['year']
        if 'rating.kp' in filters:
            params['rating.kp'] = filters['rating.kp']
        if 'countries.name' in filters:
            params['countries.name'] = filters['countries.name']

        try:
            async with ClientSession() as session:
                response = await session.get(
                    "https://api.poiskkino.dev/v1.5/movie",
                    headers={'X-API-KEY': self.__api_key},
                    params=params,
                )
                data = await response.json()
                return [_to_entity(i) for i in data.get('docs', [])]
        except Exception as e:
            logger.error(f'Ошибка внешнего API - {e}')
            raise MovieSearchProviderError('Ошибка обращения к api') from e