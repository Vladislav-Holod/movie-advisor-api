from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update

from app.schemas.schemas import UserProfile, UserUpdateProfile
from db_depends import get_async_db
from app.models import UserModel,UserProfileModel
from auth import (get_current_user)

router = APIRouter(
    prefix='/profile',
    tags=['user_profile']
)


@router.get('/me', response_model=UserProfile)
async def get_my_profile(db: AsyncSession = Depends(get_async_db),
                         current_user: UserModel = Depends(get_current_user)):
    stmt_profile = await db.scalar(select(UserProfileModel).
                                   where(UserProfileModel.user_id == current_user.id))

    if stmt_profile is None:
        raise HTTPException(status_code=400, detail='Profile is not found')
    return stmt_profile


@router.put('/me', response_model=UserProfile)
async def update_my_profile(profile_user: UserUpdateProfile,
                            db: AsyncSession =Depends(get_async_db),
                            current_user: UserModel = Depends(get_current_user)):
    profile_stmt = await db.scalar(select(UserProfileModel).where(UserProfileModel.user_id == current_user.id))
    if profile_stmt is None:
        raise HTTPException(status_code=400, detail='Profile is not found error auth')

    update_data = profile_user.model_dump(exclude_unset=True)
    await db.execute(
        update(UserProfileModel).where(UserProfileModel.user_id == current_user.id).values(
            **update_data
        )
    )
    await db.commit()
    await db.refresh(profile_stmt)
    return profile_stmt