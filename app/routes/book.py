from fastapi import APIRouter, HTTPException, status

from app.schemas import (BookPrompt,
                         RecommendResponse)
from app.serveces.recomend_book import recommend_book

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
