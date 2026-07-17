from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.user_history import GetTaskStatusUseCase, HistoryNotFoundError
from app.domain.entities.movie import Movie as MovieEntity
from app.infrastructure.database.repositories.movie_repository import MovieRepository
from app.infrastructure.database.repositories.user_history_repository import UserHistoryRepository
from app.infrastructure.database.session import get_async_db
from app.presentation.dependencies import get_current_user
from app.presentation.schemas.movie_schemas import Movie as MovieSchema

router = APIRouter(prefix='/movie', tags=['movies'])


def movie_to_schema(movie: MovieEntity) -> MovieSchema:
    return MovieSchema(
        id=movie.id, id_pois=movie.id_pois, name_movie=movie.name_movie,
        year=movie.year, genres=movie.genres, description=movie.description,
        poster_image=movie.poster_image, movieLength=movie.movie_length,
        rating=movie.rating, reason=movie.reason,
    )


@router.get('', response_model=list[MovieSchema])
async def get_movie(db: AsyncSession = Depends(get_async_db)):
    repo = MovieRepository(db)
    movies = await repo.list_all()
    return [movie_to_schema(m) for m in movies]


@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=MovieSchema)
async def create_new_movie(movie: MovieSchema, db: AsyncSession = Depends(get_async_db)):
    repo = MovieRepository(db)
    existing = await repo.get_by_name(movie.name_movie)
    if existing is not None:
        raise HTTPException(status_code=404, detail='The movie was created a long time ago')

    entity = MovieEntity(
        id=None, id_pois=movie.id_pois, name_movie=movie.name_movie, year=movie.year,
        genres=movie.genres, description=movie.description, poster_image=movie.poster_image,
        movie_length=movie.movieLength, rating=movie.rating,
    )
    created = await repo.create(entity)
    await db.commit()
    return movie_to_schema(created)


def get_task_status_use_case(db: AsyncSession = Depends(get_async_db)) -> GetTaskStatusUseCase:
    return GetTaskStatusUseCase(UserHistoryRepository(db))


@router.get('/tasks/{task_id}')
async def get_task_status(
    task_id: str,
    current_user=Depends(get_current_user),
    use_case: GetTaskStatusUseCase = Depends(get_task_status_use_case),
):
    try:
        history = await use_case.execute(task_id, current_user.id)
    except HistoryNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")

    if history.status == "success":
        return {'status': history.status, 'movies': [movie_to_schema(m) for m in history.movie_recommend]}
    return {'status': history.status}