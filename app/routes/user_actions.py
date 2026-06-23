from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.schemas.schemas import  Movie
from db_depends import get_async_db
from app.models import UserProfileModel, MovieModel
from auth import (get_current_user)

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
async def get_liked_books(db: AsyncSession = Depends(get_async_db),
                          current_user=Depends(get_current_user)):
    profile_user = await db.scalar(select(UserProfileModel).
    options(selectinload(UserProfileModel.liked_movie)).where(
        UserProfileModel.user_id == current_user.id
    ))
    if profile_user is None:
        raise HTTPException(status_code=404, detail='likes not found')

    return profile_user.liked_movie or []

