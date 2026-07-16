from fastapi import APIRouter, Depends, HTTPException,UploadFile, File,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update
import aiofiles
import os
import uuid

from app.schemas.schemas import UserProfile, UserUpdateProfile
from app.db_depends import get_async_db
from app.models import UserModel,UserProfileModel
from app.auth import (get_current_user)



router = APIRouter(
    prefix='/profile',
    tags=['user_profile']
)

ALLOWED_FILE_EXTENSIONS = ['.jpg', '.jpeg', '.png',]
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

if not os.path.exists('profile_images'):
    os.makedirs('profile_images')


@router.get('/me', response_model=UserProfile)
async def get_my_profile(db: AsyncSession = Depends(get_async_db),
                         current_user: UserModel = Depends(get_current_user)):
    stmt_profile = await db.scalar(select(UserProfileModel).
                                   where(UserProfileModel.user_id == current_user.id))

    if stmt_profile is None:
        raise HTTPException(status_code=400, detail='Profile is not found')

    return UserProfile(
        id=stmt_profile.id,
        name=stmt_profile.name,
        favorite_genres=stmt_profile.favorite_genres,
        about_me=stmt_profile.about_me,
        user_id=stmt_profile.user_id,
        created_at=stmt_profile.created_at,
        image_id=stmt_profile.image_id,
        image_url=(
            f"/profile_images/{stmt_profile.image_id}"
            if stmt_profile.image_id
            else None
        ),
    )

@router.put('/me', response_model=UserProfile)
async def update_my_profile(profile_user: UserUpdateProfile,
                            db: AsyncSession =Depends(get_async_db),
                            current_user: UserModel = Depends(get_current_user)):
    profile_stmt = await db.scalar(select(UserProfileModel).where(UserProfileModel.user_id == current_user.id))
    if profile_stmt is None:
        raise HTTPException(status_code=400, detail='Profile is not found error auth')

    if profile_user.name is not None:
        profile_name_checking = await db.scalar(select(UserProfileModel).
                                                where(UserProfileModel.name == profile_user.name,
                                                              UserProfileModel.user_id != current_user.id))
        if profile_name_checking is not None:
            raise HTTPException(status_code=400, detail='Profile name already exists')

    update_data = profile_user.model_dump(exclude_unset=True)
    await db.execute(
        update(UserProfileModel).where(UserProfileModel.user_id == current_user.id).values(
            **update_data
        )
    )
    await db.commit()
    await db.refresh(profile_stmt)
    return profile_stmt

@router.post('/me/upload-profile-image', response_model=dict)
async def upload_profile_image(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
    file: UploadFile = File(...),
):
    filename_lower = file.filename.lower()

    file_size = getattr(file, "size", None)
    if file_size is not None and file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds the maximum limit of {MAX_FILE_SIZE / (1024 * 1024)} MB",
        )

    file_extension = os.path.splitext(filename_lower)[1]
    if file_extension not in ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension. Allowed extensions: {', '.join(ALLOWED_FILE_EXTENSIONS)}",
        )

    os.makedirs("profile_images", exist_ok=True)

    filename = uuid.uuid4().hex + file_extension
    file_location = os.path.join("profile_images", filename)

    chunk_size = 1024 * 1024  # 1 MB
    current_size = 0

    try:
        async with aiofiles.open(file_location, "wb") as f:
            while True:
                content = await file.read(chunk_size)
                if not content:
                    break
                current_size += len(content)
                if current_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"File size exceeds the maximum limit of {MAX_FILE_SIZE / (1024 * 1024)} MB",
                    )
                await f.write(content)
    except HTTPException:
        if os.path.exists(file_location):
            os.remove(file_location)
        raise
    except Exception as e:
        if os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while uploading the file: {str(e)}",
        )

    profile_stmt = await db.scalar(select(UserProfileModel).
                                   where(UserProfileModel.user_id == current_user.id))
    old_avatar = profile_stmt.image_id if profile_stmt else None

    await db.execute(
        update(UserProfileModel).where(UserProfileModel.user_id == current_user.id).values(
            image_id=filename
        )
    )
    await db.commit()

    if old_avatar:
        old_path  = os.path.join("profile_images", old_avatar)
        if os.path.exists(old_path):
            os.remove(old_path)
    
    return {
        'filename':filename,
        'content_type':file.content_type,
        'message':'Profile image uploaded successfully'
    }

