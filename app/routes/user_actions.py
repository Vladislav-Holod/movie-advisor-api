from fastapi import APIRouter, Depends, HTTPException, status,Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,desc
from sqlalchemy.orm import selectinload

from app.schemas.schemas import Movie,MovieListResponse
from app.db_depends import get_async_db
from app.models import UserProfileModel, MovieModel, UserHistoryPrompt
from app.auth import (get_current_user)
from app.schemas.schemas import UserGroupHistory,UserHistory
from app.models.association_tables import user_profile_liked_movie  

router = APIRouter(
    prefix='/actions',
    tags=['user_actions']
)


@router.post('/like/{movie_id}', response_model=Movie, status_code=status.HTTP_200_OK)
async def user_like_book(movie_id: int,
                         db: AsyncSession = Depends(get_async_db),
                         current_user=Depends(get_current_user)):
    profile_user = await db.scalar(
        select(UserProfileModel)
        .options(selectinload(UserProfileModel.liked_movie))
        .where(UserProfileModel.user_id == current_user.id)
    )
    if profile_user is None or profile_user.name is None:
        raise HTTPException(status_code=404, detail='Profile not found, auth pls')

    movie = await db.scalar(select(MovieModel).where(MovieModel.id == movie_id))
    if movie is None:
        raise HTTPException(status_code=404, detail='book is not found')

    if movie in profile_user.liked_movie:
        raise HTTPException(status_code=400, detail='Book already liked')

    profile_user.liked_movie.append(movie)
    await db.commit()
    await db.refresh(movie)
    return movie


@router.get('/like/my', response_model=MovieListResponse)
async def get_liked_movie(db: AsyncSession = Depends(get_async_db),
                          current_user=Depends(get_current_user),
                          cursor: int | None = Query(default=None, description="ID последней записи с прошлой страницы"),
                          limit: int = Query(default=10, ge=1, le=50, description="Сколько записей вернуть")):
    
    profile_user = await db.scalar(
        select(UserProfileModel).where(UserProfileModel.user_id == current_user.id)
    )

    if profile_user is None:
        raise HTTPException(status_code=404, detail='profile not found')

    query = (
        select(MovieModel)
        .join(user_profile_liked_movie, user_profile_liked_movie.c.movie_base_id == MovieModel.id)
        .where(user_profile_liked_movie.c.profile_id == profile_user.id)
        .order_by(MovieModel.id.desc())
    )
    if cursor:
        query = query.where(MovieModel.id < cursor)
    
    query = query.limit(limit + 1)
    result = await db.scalars(query)
    movies = result.all()  

    has_more = len(movies) > limit
    items = movies[:limit]
    next_cursor = items[-1].id if has_more and items else None
    
    return {'movies': items,
             'next_cursor': next_cursor, 
             'has_more': has_more}


@router.delete('/like/{movie_id}', response_model=dict, status_code=status.HTTP_200_OK)
async def unlike_movie(movie_id: int,
                       db: AsyncSession = Depends(get_async_db),
                       current_user=Depends(get_current_user)):
    
    profile_user = await db.scalar(select(UserProfileModel).
    options(selectinload(UserProfileModel.liked_movie)).where(
        UserProfileModel.user_id == current_user.id
    ))

    if profile_user is None:
        raise HTTPException(status_code=404, detail='likes not found')
    movie = await db.scalar(select(MovieModel).where(MovieModel.id == movie_id))
    if movie is None:
        raise HTTPException(status_code=404, detail='movie is None')
    if movie not in profile_user.liked_movie:
        raise HTTPException(status_code=400, detail='Movie not in liked')

    profile_user.liked_movie.remove(movie)
    await db.commit()
    return {'delete': 'ok'}


@router.get('/history', response_model=UserGroupHistory)
async def get_history_user(
        current_user=Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db),
        cursor: int | None = Query(default=None, description="ID последней записи с прошлой страницы"),
        limit: int = Query(default=10, ge=1, le=50, description="Сколько записей вернуть"),
):
    query =(
        select(UserHistoryPrompt)
        .options(selectinload(UserHistoryPrompt.movie_recommend))
        .where(UserHistoryPrompt.user_id == current_user.id)
        .where(UserHistoryPrompt.movie_recommend is not None)
        .order_by(UserHistoryPrompt.created_at.desc())
    )
    if cursor:
        query = query.filter(UserHistoryPrompt.id < cursor)
    query = query.limit(limit+1)
    result = await db.scalars(query)
    history = result.all()

    has_more = len(history) > limit
    items = history[:limit]
    next_cursor = items[-1].id if has_more and items else None

    return {'history': history, 
            'next_cursor': next_cursor, 
            'has_more': has_more}


@router.get('/history/{history_id}', response_model=UserHistory)
async def get_history_user_id(history_id:int,
        current_user=Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
):
    history_ = await db.scalar(select(UserHistoryPrompt).
                              where(UserHistoryPrompt.user_id == current_user.id).
                              where(UserHistoryPrompt.id == history_id))

    if history_ is None:
        raise HTTPException(status_code=400, detail='history not found')

    return {'history': history_}