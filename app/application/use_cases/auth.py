from app.core import security
from app.domain.entities.user import User
from app.domain.entities.user_profile import UserProfile
from app.domain.repositories.user_repository import AbstractUserRepository
from app.domain.repositories.user_profile_repository import AbstractUserProfileRepository


class EmailAlreadyRegisteredError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class RegisterUserUseCase:
    def __init__(
        self,
        user_repo: AbstractUserRepository,
        profile_repo: AbstractUserProfileRepository,
    ):
        self.user_repo = user_repo
        self.profile_repo = profile_repo

    async def execute(self, email: str, password: str) -> User:
        existing = await self.user_repo.get_active_by_email(email)
        if existing is not None:
            raise EmailAlreadyRegisteredError()

        user = User(
            id=None,
            email=email,
            hashed_password=security.hash_password(password),
            is_active=True,
        )
        created_user = await self.user_repo.create(user)

        await self.profile_repo.create_empty(created_user.id)

        return created_user


class LoginUseCase:
    def __init__(self, user_repo: AbstractUserRepository):
        self.user_repo = user_repo

    async def execute(self, email: str, password: str) -> dict:
        user = await self.user_repo.get_active_by_email(email)
        if user is None or not security.verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()

        access_token = security.create_access_token(data={'sub': user.email, 'id': user.id})
        refresh_token = security.create_refresh_token(data={'sub': user.email, 'id': user.id})
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer',
        }


class RefreshTokenUseCase:
    def __init__(self, user_repo: AbstractUserRepository):
        self.user_repo = user_repo

    async def execute(self, refresh_token: str) -> dict:
        payload = security.decode_token(refresh_token)  # кидает jwt.PyJWTError наверх
        email = payload.get('sub')
        token_type = payload.get('token_type')
        if email is None or token_type != 'refresh':
            raise InvalidCredentialsError()

        user = await self.user_repo.get_active_by_email(email)
        if user is None:
            raise InvalidCredentialsError()

        new_access_token = security.create_access_token(data={'sub': user.email, 'id': user.id})
        new_refresh_token = security.create_refresh_token(data={'sub': user.email, 'id': user.id})
        return {
            'access_token': new_access_token,
            'refresh_token': new_refresh_token,
            'token_type': 'bearer',
        }


class GetNewAccessTokenUseCase:
    def __init__(self, user_repo: AbstractUserRepository):
        self.user_repo = user_repo

    async def execute(self, refresh_token: str) -> dict:
        payload = security.decode_token(refresh_token)
        email = payload.get('sub')
        token_type = payload.get('token_type')
        if email is None or token_type != 'refresh':
            raise InvalidCredentialsError()

        user = await self.user_repo.get_active_by_email(email)
        if user is None:
            raise InvalidCredentialsError()

        access_token = security.create_access_token(data={'sub': user.email, 'id': user.id})
        return {'access-token': access_token, 'token_type': 'bearer'}