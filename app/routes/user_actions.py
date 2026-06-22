from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.schemas.schemas import UserProfile, UserUpdateProfile, Book
from db_depends import get_async_db
from app.models import UserModel, UserProfileModel, BookModel
from auth import (get_current_user)

router = APIRouter(
    prefix='/actions',
    tags=['actions']
)


@router.post('/like/{book_id}', response_model=Book, status_code=status.HTTP_200_OK)
async def user_like_book(book_id: int,
                         db: AsyncSession = Depends(get_async_db),
                         current_user=Depends(get_current_user)):
    profile_user = await db.scalar(
        select(UserProfileModel)
        .options(selectinload(UserProfileModel.liked_books))
        .where(UserProfileModel.user_id == current_user.id)
    )
    if profile_user is None or profile_user.name is None:
        raise HTTPException(status_code=404, detail='Profile not found, auth pls')

    book = await db.scalar(select(BookModel).where(BookModel.id == book_id))
    if book is None:
        raise HTTPException(status_code=404, detail='book is not found')

    if book in profile_user.liked_books:
        raise HTTPException(status_code=400, detail='Book already liked')

    profile_user.liked_books.append(book)
    await db.commit()
    await db.refresh(book)
    return book


@router.get('/like/my', response_model=list[Book])
async def get_liked_books(db: AsyncSession = Depends(get_async_db),
                          current_user=Depends(get_current_user)):
    profile_user = await db.scalar(select(UserProfileModel).
    options(selectinload(UserProfileModel.liked_books)).where(
        UserProfileModel.user_id == current_user.id
    ))
    if profile_user is None:
        raise HTTPException(status_code=404, detail='likes not found')

    return profile_user.liked_books or []

