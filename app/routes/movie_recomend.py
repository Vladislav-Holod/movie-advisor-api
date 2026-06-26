from fastapi import APIRouter, Depends
from app.schemas.schemas import Movie
from app.dependencies import ai_client
from app.dependencies import api_kinopoisk
import asyncio
from app.db_depends import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import MovieModel
from sqlalchemy import select
from app.auth import (get_current_user)
from app.schemas.schemas import MoviePrompt
router = APIRouter(
    prefix='/movie',
    tags=['AI']
)


@router.post('/recommend', response_model=list[Movie])
async def recommend_movie(prompt: MoviePrompt,
                          db: AsyncSession = Depends(get_async_db),
                          current_user=Depends(get_current_user)):

    filter_sets = await ai_client.ai_response_search_filters(prompt.prompt)
    tasks = [api_kinopoisk.search_by_filters(f, limit=15) for f in filter_sets]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    seen = set()
    all_movies = []
    for movies in results:
        if isinstance(movies, Exception):
            continue
        for movie in movies:
            if movie.id_pois not in seen:
                seen.add(movie.id_pois)
                all_movies.append(movie)
    result_movie_for_client = await ai_client.ai_search_best_movie(all_movies, prompt.prompt)

    movie_ids = [movie.id_pois for movie in result_movie_for_client]

    existing_ids = set(
        (await db.execute(
            select(MovieModel.id_pois).where(
                MovieModel.id_pois.in_(movie_ids)))).scalars().all())
    new_movies = [
        MovieModel(**movie.model_dump())
        for movie in result_movie_for_client
        if movie.id_pois not in existing_ids]

    if new_movies:
        db.add_all(new_movies)
        await db.commit()

    return result_movie_for_client
