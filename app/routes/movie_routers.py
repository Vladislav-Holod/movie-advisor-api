from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.schemas.schemas import (Movie)
from app.db_depends import get_async_db
from app.models.users_history import UserHistoryPrompt, TaskStatus
from app.auth import get_current_user
from app.db_depends import get_async_db
from app.models import MovieModel

router = APIRouter(
    prefix='/movie',
    tags=['movies']
)

@router.get('', response_model=list[Movie])
async def get_movie(db: AsyncSession = Depends(get_async_db)):
    movie_list = (await db.scalars(select(MovieModel))).all()
    return movie_list


@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_new_movie(movie: Movie,
                           db: AsyncSession = Depends(get_async_db)):
    movie_result = await db.scalar(select(MovieModel).where(MovieModel.name_movie == movie.name_movie))
    if movie_result is not None:
        raise HTTPException(status_code=404, detail='The movie was created a long time ago')
    movie = MovieModel(**movie.model_dump())
    db.add(movie)
    await  db.commit()
    await db.refresh(movie)
    return movie

@router.get('/tasks/{task_id}')
async def get_task_status(task_id:str,
                          db:AsyncSession = Depends(get_async_db),
                          current_user = Depends(get_current_user)):
    history_result = await db.scalar(
        select(UserHistoryPrompt)
        .options(selectinload(UserHistoryPrompt.movie_recommend))
        .where(
            UserHistoryPrompt.task_id == task_id,
            UserHistoryPrompt.user_id == current_user.id,
        )
    )

    if history_result is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if history_result.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this task")
    if history_result.status == TaskStatus.SUCCESS:
        return {'status':history_result.status, 
                'movies':history_result.movie_recommend}
    else:
        return {'status':history_result.status}