from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_async_db
from app.infrastructure.database.repositories.movie_repository import MovieRepository
from app.infrastructure.database.repositories.user_profile_repository import UserProfileRepository
from app.infrastructure.database.repositories.user_history_repository import UserHistoryRepository

from app.application.use_cases.movie_likes import (
    LikeMovieUseCase,
    UnlikeMovieUseCase,
    GetLikedMoviesUseCase,
    ProfileNotFoundError,
    MovieNotFoundError,
    AlreadyLikedError,
    NotLikedError,
)
from app.application.use_cases.user_history import (
    GetHistoryListUseCase,
    GetHistoryByIdUseCase,
    HistoryNotFoundError,
)

from app.presentation.dependencies import get_current_user
from app.presentation.schemas.movie_schemas import Movie, MovieListResponse
from app.presentation.schemas.history_schemas import (
    UserGroupHistory,
    UserHistory as UserHistoryOut,
)

router = APIRouter(prefix='/actions', tags=['user_actions'])


# ---------- DI-фабрики use case'ов ----------

def get_like_use_case(db: AsyncSession = Depends(get_async_db)) -> LikeMovieUseCase:
    return LikeMovieUseCase(UserProfileRepository(db), MovieRepository(db))


def get_unlike_use_case(db: AsyncSession = Depends(get_async_db)) -> UnlikeMovieUseCase:
    return UnlikeMovieUseCase(UserProfileRepository(db), MovieRepository(db))


def get_liked_use_case(db: AsyncSession = Depends(get_async_db)) -> GetLikedMoviesUseCase:
    return GetLikedMoviesUseCase(UserProfileRepository(db))


def get_history_list_use_case(db: AsyncSession = Depends(get_async_db)) -> GetHistoryListUseCase:
    return GetHistoryListUseCase(UserHistoryRepository(db))


def get_history_by_id_use_case(db: AsyncSession = Depends(get_async_db)) -> GetHistoryByIdUseCase:
    return GetHistoryByIdUseCase(UserHistoryRepository(db))


# ---------- Likes ----------

@router.post('/like/{movie_id}', response_model=Movie, status_code=status.HTTP_200_OK)
async def user_like_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_user),
    use_case: LikeMovieUseCase = Depends(get_like_use_case),
):
    try:
        movie = await use_case.execute(current_user.id, movie_id)
        await db.commit()
        return movie
    except ProfileNotFoundError:
        raise HTTPException(status_code=404, detail='Profile not found, auth pls')
    except MovieNotFoundError:
        raise HTTPException(status_code=404, detail='movie is not found')
    except AlreadyLikedError:
        raise HTTPException(status_code=400, detail='Movie already liked')


@router.delete('/like/{movie_id}', response_model=dict, status_code=status.HTTP_200_OK)
async def unlike_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_user),
    use_case: UnlikeMovieUseCase = Depends(get_unlike_use_case),
):
    try:
        await use_case.execute(current_user.id, movie_id)
        await db.commit()
        return {'delete': 'ok'}
    except ProfileNotFoundError:
        raise HTTPException(status_code=404, detail='likes not found')
    except MovieNotFoundError:
        raise HTTPException(status_code=404, detail='movie is None')
    except NotLikedError:
        raise HTTPException(status_code=400, detail='Movie not in liked')


@router.get('/like/my', response_model=MovieListResponse)
async def get_liked_movie(
    current_user=Depends(get_current_user),
    cursor: int | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=50),
    use_case: GetLikedMoviesUseCase = Depends(get_liked_use_case),
):
    try:
        movies, next_cursor, has_more = await use_case.execute(current_user.id, cursor, limit)
        return {'movies': movies, 'next_cursor': next_cursor, 'has_more': has_more}
    except ProfileNotFoundError:
        raise HTTPException(status_code=404, detail='profile not found')


# ---------- History ----------

@router.get('/history', response_model=UserGroupHistory)
async def get_history_user(
    current_user=Depends(get_current_user),
    cursor: int | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=50),
    use_case: GetHistoryListUseCase = Depends(get_history_list_use_case),
):
    items, next_cursor, has_more = await use_case.execute(current_user.id, cursor, limit)
    return {'history': items, 'next_cursor': next_cursor, 'has_more': has_more}


@router.get('/history/{history_id}', response_model=UserHistoryOut)
async def get_history_user_id(
    history_id: int,
    current_user=Depends(get_current_user),
    use_case: GetHistoryByIdUseCase = Depends(get_history_by_id_use_case),
):
    try:
        history = await use_case.execute(history_id, current_user.id)
        return {'history': history}
    except HistoryNotFoundError:
        raise HTTPException(status_code=400, detail='history not found')