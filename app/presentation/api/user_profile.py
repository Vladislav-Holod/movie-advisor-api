from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_async_db
from app.infrastructure.database.repositories.user_profile_repository import UserProfileRepository
from app.infrastructure.files.local_storage import LocalFileStorage, FileTooLargeError
from app.application.use_cases.user_profile import (
    GetMyProfileUseCase, UpdateMyProfileUseCase, UploadProfileImageUseCase,
    ProfileNotFoundError, ProfileNameTakenError, InvalidFileExtensionError,
)
from app.presentation.dependencies import get_current_user
from app.presentation.schemas.user_schemas import UserProfile as UserProfileSchema, UserUpdateProfile

router = APIRouter(prefix='/profile', tags=['user_profile'])

_file_storage = LocalFileStorage()


def get_profile_repo(db: AsyncSession = Depends(get_async_db)) -> UserProfileRepository:
    return UserProfileRepository(db)


def profile_to_schema(profile) -> UserProfileSchema:
    return UserProfileSchema(
        id=profile.id, name=profile.name, favorite_genres=profile.favorite_genres,
        about_me=profile.about_me, user_id=profile.user_id, created_at=profile.created_at,
        image_id=profile.image_id,
        image_url=f"/profile_images/{profile.image_id}" if profile.image_id else None,
    )


@router.get('/me', response_model=UserProfileSchema)
async def get_my_profile(
    current_user=Depends(get_current_user),
    repo: UserProfileRepository = Depends(get_profile_repo),
):
    try:
        profile = await GetMyProfileUseCase(repo).execute(current_user.id)
        return profile_to_schema(profile)
    except ProfileNotFoundError:
        raise HTTPException(status_code=400, detail='Profile is not found')


@router.put('/me', response_model=UserProfileSchema)
async def update_my_profile(
    profile_data: UserUpdateProfile,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_user),
    repo: UserProfileRepository = Depends(get_profile_repo),
):
    try:
        update_data = profile_data.model_dump(exclude_unset=True)
        profile = await UpdateMyProfileUseCase(repo).execute(current_user.id, update_data)
        await db.commit()
        return profile_to_schema(profile)
    except ProfileNotFoundError:
        raise HTTPException(status_code=400, detail='Profile is not found error auth')
    except ProfileNameTakenError:
        raise HTTPException(status_code=400, detail='Profile name already exists')


@router.post('/me/upload-profile-image', response_model=dict)
async def upload_profile_image(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
    repo: UserProfileRepository = Depends(get_profile_repo),
    file: UploadFile = File(...),
):
    use_case = UploadProfileImageUseCase(repo, _file_storage)
    try:
        new_filename = await use_case.execute(current_user.id, file.filename, file.read)
        await db.commit()
        return {
            'filename': new_filename,
            'content_type': file.content_type,
            'message': 'Profile image uploaded successfully',
        }
    except ProfileNotFoundError:
        raise HTTPException(status_code=400, detail='Profile is not found')
    except InvalidFileExtensionError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension. Allowed extensions: {', '.join(['.jpg', '.jpeg', '.png'])}",
        )
    except FileTooLargeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the maximum limit of 5 MB",
        )