from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.schemas import (MoviePrompt, RecommendResponse, Movie)
from app.services.recomend_movie import recommend_movie
from db_depends import get_async_db
from app.models import MovieModel

router = APIRouter(
    prefix='/movie',
    tags=['movies']
)

@router.post('/recommend', response_model=RecommendResponse)
async def get_book_recommend(prompt: MoviePrompt):
    try:
        return await recommend_movie(prompt.prompt)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=e)


@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_new_movie(movie: Movie,
                          db: AsyncSession = Depends(get_async_db)):
    movie_result = await db.scalar(select(MovieModel).where(MovieModel.name_movie == movie.name_movie))
    if movie_result is not None:
        raise HTTPException(status_code=404, detail='The movie was created a long time ago')
    movie = MovieModel(**movie.model_dump())
    db.add(movie)
    await  db.commit()
    await db.refresh(movie)
    return movie
