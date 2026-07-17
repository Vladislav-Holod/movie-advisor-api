from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.movie import Movie
from app.domain.repositories.movie_repository import AbstractMovieRepository
from app.infrastructure.database.models.movie_models import MovieModel


def _to_entity(model: MovieModel) -> Movie:
    return Movie(
        id=model.id, id_pois=model.id_pois, name_movie=model.name_movie,
        year=model.year, genres=model.genres, description=model.description,
        poster_image=model.poster_image, movie_length=model.movieLength,
        rating=model.rating,
    )


class MovieRepository(AbstractMovieRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, movie_id: int) -> Movie | None:
        model = await self.session.get(MovieModel, movie_id)
        return _to_entity(model) if model else None

    async def get_by_name(self, name: str) -> Movie | None:
        result = await self.session.scalar(
            select(MovieModel).where(MovieModel.name_movie == name)
        )
        return _to_entity(result) if result else None

    async def list_all(self) -> list[Movie]:
        result = await self.session.scalars(select(MovieModel))
        return [_to_entity(m) for m in result.all()]

    async def create(self, movie: Movie) -> Movie:
        model = MovieModel(
            id_pois=movie.id_pois, name_movie=movie.name_movie, year=movie.year,
            genres=movie.genres, description=movie.description,
            poster_image=movie.poster_image, movieLength=movie.movie_length,
            rating=movie.rating,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return _to_entity(model)

    async def get_existing_pois_ids(self, pois_ids: list[int]) -> set[int]:
        result = await self.session.execute(
            select(MovieModel.id_pois).where(MovieModel.id_pois.in_(pois_ids))
        )
        return set(result.scalars().all())

    async def bulk_create(self, movies: list[Movie]) -> None:
        models = [
            MovieModel(
                id_pois=m.id_pois, name_movie=m.name_movie, year=m.year,
                genres=m.genres, description=m.description, poster_image=m.poster_image,
                movieLength=m.movie_length, rating=m.rating,
            )
            for m in movies
        ]
        self.session.add_all(models)
        await self.session.flush()