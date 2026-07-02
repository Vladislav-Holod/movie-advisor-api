from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.movie_models import MovieModel
from app.models.users_history import UserHistoryPrompt,TaskStatus
import asyncio

async def recommend_movie(prompt_text: str ,
                          db: AsyncSession,
                          task_id:str,
                          ai_client,
                          api_kinopoisk
                          )->None:
    
    history_response = await db.scalar(
        select(UserHistoryPrompt)
        .where(UserHistoryPrompt.task_id == task_id)
        .options(selectinload(UserHistoryPrompt.movie_recommend))
    )
    if history_response is None:
        raise ValueError(f"No UserHistoryPrompt found with task_id: {task_id}")
    
    history_response.status = TaskStatus.RUNNING
    await db.commit()

    filter_sets = await ai_client.ai_response_search_filters(prompt_text)
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

    result_movie_for_client = await ai_client.ai_search_best_movie(all_movies, prompt_text)
    movie_ids = [movie.id_pois for movie in result_movie_for_client]

    existing_ids = set(
        (await db.execute(
            select(MovieModel.id_pois).where(
                MovieModel.id_pois.in_(movie_ids)))).scalars().all())
    new_movies = [
        MovieModel(**movie.model_dump(exclude={'reason', 'id'}))
        for movie in result_movie_for_client
        if movie.id_pois not in existing_ids
    ]
    if new_movies:
        db.add_all(new_movies)
        await db.flush()  # Flush to get IDs for new movies
    
    movies = (
        await db.scalars(
            select(MovieModel).where(MovieModel.id_pois.in_(movie_ids))
        )
    ).all()

    history_response.movie_recommend = movies
    history_response.response = 'Response by AI'
    history_response.status = TaskStatus.SUCCESS
    await db.commit()