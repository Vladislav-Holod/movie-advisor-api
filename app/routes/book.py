from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import json
from app.schemas.schemas import (BookPrompt, RecommendResponse, Book)
from app.services.recomend_book import recommend_book
from db_depends import get_async_db
from app.models import BookModel

router = APIRouter(
    prefix='/books',
    tags=['books']
)


@router.post('/recommend', response_model=RecommendResponse)
async def get_book_recommend(prompt: BookPrompt):
    try:
        return await recommend_book(prompt.prompt)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=e)


@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_new_book(book: Book,
                          db: AsyncSession = Depends(get_async_db)):
    books_result = await db.scalar(select(BookModel).where(BookModel.title == book.title))
    if books_result is not None:
        raise HTTPException(status_code=404, detail='The book was created a long time ago')
    book = BookModel(**book.model_dump())
    db.add(book)
    await  db.commit()
    await db.refresh(book)
    return book
