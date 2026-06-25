from fastapi import APIRouter
from app.schemas.schemas import Movie
from app.dependencies import ai_client
from app.dependencies import api_kinopoisk
from typing import List
import asyncio

router = APIRouter(
    prefix='/movie/recommend',
    tags=['AI']
)


@router.post('/', response_model=list)
async def recommend_movie(prompt: str):
    filter_sets = await ai_client.ai_response(prompt)
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
    return all_movies
