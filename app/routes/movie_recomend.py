from fastapi import APIRouter, Depends,HTTPException
from app.schemas.schemas import Movie
from app.dependencies import ai_client
from app.dependencies import api_kinopoisk
from app.db_depends import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import MovieModel,UserHistoryPrompt
from sqlalchemy import select
from app.auth import (get_current_user)
from app.schemas.schemas import MoviePrompt
import asyncio
import uuid
from app.models.users_history import UserHistoryPrompt,TaskStatus
from app.tasks.movie_task import recommend_movie_task
router = APIRouter(
    prefix='/movie',
    tags=['AI']
)




@router.post('/recommend')
async def recommend_movie_endpoint(prompt: MoviePrompt,
                                    db: AsyncSession = Depends(get_async_db),
                                    current_user = Depends(get_current_user)):
    
    task_id = str(uuid.uuid4())   # Generate a unique task ID Race condition Prevention

    history = UserHistoryPrompt(
        task_id=task_id,
        prompt=prompt.prompt,
        response='',
        status=TaskStatus.PENDING,
        user_id=current_user.id,
        movie_recommend=[]
    )
    db.add(history)
    await db.commit()                
    recommend_movie_task.delay(task_id, prompt.prompt)  

    return {'task_id': task_id}

@router.get('/recommend/{task_id}')
async def get_task_status(task_id:str,
                          db:AsyncSession = Depends(get_async_db),
                          current_user = Depends(get_current_user)):
    history_result = await db.scalar(select(UserHistoryPrompt).
                                     where(UserHistoryPrompt.task_id == task_id))
    if history_result is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if history_result.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this task")
    if history_result.status == TaskStatus.SUCCESS:
        return {'status':history_result.status, 
                'movies':history_result.movie_recommend}
    else:
        return {'status':history_result.status}