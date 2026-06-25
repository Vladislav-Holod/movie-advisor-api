import json
from typing import Any

from app.services.providers_llm.base import LLMProvider
from loguru import logger
from fastapi import HTTPException, status


class AIService:
    def __init__(self, provider: LLMProvider):
        self.__provider = provider

    async def ai_response_search_filters(self, text: str) -> list:
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

        Примеры стратегий:
        - "мрачные криминальные триллеры" → 1й: оба жанра + рейтинг, 2й: только криминал + год, 3й: только триллер + сортировка по голосам
        - "советские комедии" → 1й: комедия + СССР, 2й: комедия + год 1950-1991
        - "страшные новые фильмы" → 1й: ужасы + новый год + рейтинг, 2й: ужасы + новый год + голоса

        Запрос пользователя: {text}
        """
        result = await self.__provider.generate(prompt)
        try:
            data = json.loads(result)
            return data['filter_sets']
        except Exception as e:
            logger.error(f'Ошибка парсинга фильтров - {e}, raw: {result}')
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail='Ошибка извлечения фильтров'
            )

    async def ai_search_best_movie(self, all_movies: list, prompt):

        movie_list = [
            {
                'id': m.id_pois,
                'name': m.name_movie,
                'year': m.year,
                'rating': m.rating,
                'genres': m.genres,
                'description': (m.description or '')[:200]
            }
            for m in all_movies
        ]

        prompt = f"""
        Пользователь ищет фильмы по запросу: "{prompt}"

        Вот список реальных фильмов из базы данных:
        {json.dumps(movie_list, ensure_ascii=False)}

        Твоя задача — выбрать 5-10 фильмов которые МАКСИМАЛЬНО точно соответствуют именно запросу пользователя.

        Верни ТОЛЬКО JSON без пояснений и markdown.

        Формат:
        {{
          "movies": [
            {{
              "id": 123,
              "reason": "почему этот фильм подходит под запрос пользователя (1 предложение на русском)"
            }}
          ]
        }}

        Правила:
        - выбирай ТОЛЬКО из предоставленного списка, никаких новых фильмов
        - сортируй по релевантности запросу — самый подходящий первым
        - в reason объясняй именно почему фильм подходит под конкретный запрос пользователя
        - если пользователь просил страшные — reason должен говорить почему именно этот фильм страшный
        - если пользователь просил про приключения — reason про приключения и т.д.
        - если ни один фильм не подходит под запрос — верни пустой список
        - не выбирай фильмы только по высокому рейтингу если они не соответствуют запросу
        """
        result = await self.__provider.generate(prompt)
        try:
            data = json.loads(result)
            selected_ids = {m['id']: m['reason'] for m in data['movies']}
            final_movies = []
            for movie in all_movies:
                if movie.id_pois in selected_ids:
                    movie.reason = selected_ids[movie.id_pois]
                    final_movies.append(movie)

            return final_movies

        except Exception as e:
            logger.error(f'Ошибка парсинга выбора фильмов - {e}, raw: {result}')
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail='Ошибка выбора фильмов'
            )
