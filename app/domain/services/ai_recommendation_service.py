import json

from loguru import logger

from app.domain.entities.movie import Movie
from app.domain.repositories.llm_provider import AbstractLLMProvider


class FilterExtractionError(Exception):
    pass


class MovieSelectionError(Exception):
    pass


class AIRecommendationService:
    def __init__(self, provider: AbstractLLMProvider):
        self._provider = provider

    async def extract_search_filters(self, text: str) -> list[dict]:
        prompt = f"""
        Ты помощник для поиска фильмов. Составь 2-3 разных набора фильтров для поиска по запросу пользователя.

        Верни ТОЛЬКО JSON без пояснений и markdown.

        Доступные поля:
        - "genres": список из ["драма", "комедия", "триллер", "ужасы", "боевик", "криминал", "мелодрама", "фантастика", "документальный", "биография", "история", "приключения", "фэнтези", "мультфильм", "аниме", "семейный", "вестерн", "спорт"]
        - "year": год или диапазон (пример: "2000-2015")
        - "rating.kp": диапазон рейтинга (пример: "7-10")
        - "type": из ["movie", "tv-series", "cartoon", "anime"]
        - "countries.name": список стран на русском
        - "sortField": из ["rating.kp", "year", "votes.kp"]
        - "sortType": "-1" или "1"

        Формат ответа:
        {{
          "filter_sets": [
            {{"genres": ["криминал", "триллер"], "rating.kp": "7-10", "sortField": "rating.kp", "sortType": "-1"}},
            {{"genres": ["криминал"], "year": "2000-2015", "sortField": "rating.kp", "sortType": "-1"}},
            {{"genres": ["триллер", "драма"], "sortField": "votes.kp", "sortType": "-1"}}
          ]
        }}

        Правила:
        - каждый набор должен быть немного разным чтобы получить разнообразные результаты
        - не дублируй одинаковые наборы
        - если запрос простой — достаточно 2 наборов
        - если сложный/многогранный — делай 3

        Запрос пользователя: {text}
        """
        result = await self._provider.generate(prompt)
        try:
            data = json.loads(result)
            return data['filter_sets']
        except Exception as e:
            logger.error(f'Ошибка парсинга фильтров - {e}, raw: {result}')
            raise FilterExtractionError() from e

    async def select_best_movies(self, all_movies: list[Movie], prompt_text: str) -> list[Movie]:
        movie_list = [
            {
                'id': m.id_pois,
                'name': m.name_movie,
                'year': m.year,
                'rating': m.rating,
                'genres': m.genres,
                'description': (m.description or '')[:200],
            }
            for m in all_movies
        ]

        prompt = f"""
        Пользователь ищет фильмы по запросу: "{prompt_text}"

        Вот список реальных фильмов из базы данных:
        {json.dumps(movie_list, ensure_ascii=False)}

        Твоя задача — выбрать 5-10 фильмов которые МАКСИМАЛЬНО точно соответствуют именно запросу пользователя.

        Верни ТОЛЬКО JSON без пояснений и markdown.

        Формат:
        {{
          "movies": [
            {{"id": 123, "reason": "почему этот фильм подходит под запрос пользователя (1 предложение на русском)"}}
          ]
        }}

        Правила:
        - выбирай ТОЛЬКО из предоставленного списка, никаких новых фильмов
        - сортируй по релевантности запросу — самый подходящий первым
        - если ни один фильм не подходит под запрос — верни пустой список
        - не выбирай фильмы только по высокому рейтингу если они не соответствуют запросу
        """
        result = await self._provider.generate(prompt)
        try:
            data = json.loads(result)
            selected = {m['id']: m['reason'] for m in data['movies']}
            final_movies = []
            for movie in all_movies:
                if movie.id_pois in selected:
                    movie.reason = selected[movie.id_pois]
                    final_movies.append(movie)
            return final_movies
        except Exception as e:
            logger.error(f'Ошибка парсинга выбора фильмов - {e}, raw: {result}')
            raise MovieSelectionError() from e