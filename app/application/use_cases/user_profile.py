import os
import uuid

from app.domain.entities.user_profile import UserProfile
from app.domain.repositories.user_profile_repository import AbstractUserProfileRepository


class ProfileNotFoundError(Exception):
    pass


class ProfileNameTakenError(Exception):
    pass


class InvalidFileExtensionError(Exception):
    pass


ALLOWED_FILE_EXTENSIONS = ['.jpg', '.jpeg', '.png']


class GetMyProfileUseCase:
    def __init__(self, profile_repo: AbstractUserProfileRepository):
        self.profile_repo = profile_repo

    async def execute(self, user_id: int) -> UserProfile:
        profile = await self.profile_repo.get_by_user_id(user_id)
        if profile is None:
            raise ProfileNotFoundError()
        return profile


class UpdateMyProfileUseCase:
    def __init__(self, profile_repo: AbstractUserProfileRepository):
        self.profile_repo = profile_repo

    async def execute(self, user_id: int, update_data: dict) -> UserProfile:
        profile = await self.profile_repo.get_by_user_id(user_id)
        if profile is None:
            raise ProfileNotFoundError()

        new_name = update_data.get('name')
        if new_name is not None:
            existing = await self.profile_repo.get_by_name(new_name)
            if existing is not None and existing.user_id != user_id:
                raise ProfileNameTakenError()

        return await self.profile_repo.update(user_id, update_data)


class UploadProfileImageUseCase:
    def __init__(self, profile_repo: AbstractUserProfileRepository, file_storage):
        self.profile_repo = profile_repo
        self.file_storage = file_storage

    def validate_extension(self, filename: str) -> str:
        ext = os.path.splitext(filename.lower())[1]
        if ext not in ALLOWED_FILE_EXTENSIONS:
            raise InvalidFileExtensionError()
        return ext

    async def execute(self, user_id: int, filename: str, read_chunk) -> str:
        profile = await self.profile_repo.get_by_user_id(user_id)
        if profile is None:
            raise ProfileNotFoundError()

        ext = self.validate_extension(filename)
        new_filename = uuid.uuid4().hex + ext
        old_avatar = profile.image_id

        await self.file_storage.save_from_stream(new_filename, read_chunk)
        await self.profile_repo.update(user_id, {'image_id': new_filename})

        if old_avatar:
            self.file_storage.delete(old_avatar)

        return new_filename