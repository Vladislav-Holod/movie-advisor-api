from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,desc
from sqlalchemy.orm import selectinload

from app.schemas.schemas import Movie
from app.db_depends import get_async_db
from app.models import UserProfileModel, MovieModel, UserHistoryPrompt
from app.auth import (get_current_user)
from app.schemas.schemas import UserGroupHistory,UserHistory

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


@router.get('/like/my', response_model=list[Movie])
async def get_liked_movie(db: AsyncSession = Depends(get_async_db),
                          current_user=Depends(get_current_user)):
    profile_user = await db.scalar(select(UserProfileModel).
    options(selectinload(UserProfileModel.liked_movie)).where(
        UserProfileModel.user_id == current_user.id
    ))
    if profile_user is None:
        raise HTTPException(status_code=404, detail='profile not found')

    return profile_user.liked_movie or []


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
        db: AsyncSession = Depends(get_async_db)
):
    result = await db.scalars(
        select(UserHistoryPrompt)
        .options(selectinload(UserHistoryPrompt.movie_recommend))
        .where(UserHistoryPrompt.user_id == current_user.id)
        .where(UserHistoryPrompt.movie_recommend != None)
        .order_by(UserHistoryPrompt.created_at.desc())
    )

    history = result.all()
    if history is None:
        raise HTTPException(status_code=400, detail='history error')

    return {'history': history}


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