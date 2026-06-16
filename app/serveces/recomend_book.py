from typing import Any, Coroutine

from app.serveces.external_api import gemini_response
import requests
from fastapi import HTTPException, status


async def open_library_search(prompt: str, topic: str):
    books_search = []
    try:
        response = requests.get("https://openlibrary.org/search.json", params={'q': topic})
        if response.status_code == 200:
            data = response.json()
            for b in data['docs'][:5]:
                books_search.append(
                    {
                        "name_book": b.get("title"),
                        "author": ", ".join(b.get("author_name", [])) if b.get("author_name") else None,
                        "image": f"https://covers.openlibrary.org/b/id/{b.get('cover_i')}-L.jpg"
                        if b.get("cover_i") else None
                    })

    except:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail='Open library не отвечает ')

    result = {'prompt': prompt,
              'books': books_search}
    return result


async def recommend_book(prompt: str) -> dict[str, list]:
    """
    Функция для запроса в gemeni для определния тематики далее ищет через
    OpenLibrary книги и отдает словарь по pydantic модели
    """
    topic_data = await gemini_response(prompt)
    topic = topic_data["topic"]
    result = await open_library_search(prompt, topic)
    result['topic'] = topic
    return result
