import asyncio

from app.domain.entities.user_history import TaskStatus
from app.domain.repositories.movie_repository import AbstractMovieRepository
from app.domain.repositories.movie_search_provider import AbstractMovieSearchProvider
from app.domain.repositories.user_history_repository import AbstractUserHistoryRepository
from app.domain.services.ai_recommendation_service import AIRecommendationService


class MarkTaskRunningUseCase:
    def __init__(self, history_repo: AbstractUserHistoryRepository):
        self.history_repo = history_repo

    async def execute(self, task_id: str) -> None:
        await self.history_repo.set_status(task_id, TaskStatus.RUNNING)


class RecommendMovieUseCase:
    def __init__(
        self,
        history_repo: AbstractUserHistoryRepository,
        movie_repo: AbstractMovieRepository,
        search_provider: AbstractMovieSearchProvider,
        ai_service: AIRecommendationService,
    ):
        self.history_repo = history_repo
        self.movie_repo = movie_repo
        self.search_provider = search_provider
        self.ai_service = ai_service

    async def execute(self, task_id: str, prompt_text: str) -> None:
        filter_sets = await self.ai_service.extract_search_filters(prompt_text)

        tasks = [self.search_provider.search_by_filters(f, limit=15) for f in filter_sets]
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

        selected_movies = await self.ai_service.select_best_movies(all_movies, prompt_text)
        movie_ids = [m.id_pois for m in selected_movies]

        existing_ids = await self.movie_repo.get_existing_pois_ids(movie_ids)
        new_movies = [m for m in selected_movies if m.id_pois not in existing_ids]
        if new_movies:
            await self.movie_repo.bulk_create(new_movies)

        await self.history_repo.complete(task_id, response='Response by AI', movie_ids=movie_ids)