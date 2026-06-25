from fastapi import APIRouter
from app.schemas.schemas import Movie
from app.dependencies import ai_client
from app.dependencies import api_kinopoisk
from typing import List
router = APIRouter(
    prefix='/movie/recommend',
    tags=['AI']
)


@router.post('/', response_model=list)
async def recommend_movie(prompt: str):
    result_topic = await ai_client.ai_response(prompt)
    # result_recommend = await api_kinopoisk.search(result_topic)
    return result_topic
