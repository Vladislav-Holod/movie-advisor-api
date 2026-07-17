from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from app.infrastructure.database.session import get_async_db
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.database.repositories.user_profile_repository import UserProfileRepository
from app.application.use_cases.auth import (
    RegisterUserUseCase,
    LoginUseCase,
    RefreshTokenUseCase,
    GetNewAccessTokenUseCase,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
)
from app.presentation.schemas.user_schemas import UserCreate, User as UserSchema
from app.presentation.schemas.auth_schemas import RefreshTokenRequest

router = APIRouter(prefix='/user', tags=['user_auth'])


def get_register_use_case(db: AsyncSession = Depends(get_async_db)) -> RegisterUserUseCase:
    return RegisterUserUseCase(UserRepository(db), UserProfileRepository(db))


def get_login_use_case(db: AsyncSession = Depends(get_async_db)) -> LoginUseCase:
    return LoginUseCase(UserRepository(db))


def get_refresh_use_case(db: AsyncSession = Depends(get_async_db)) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(UserRepository(db))


def get_new_access_token_use_case(db: AsyncSession = Depends(get_async_db)) -> GetNewAccessTokenUseCase:
    return GetNewAccessTokenUseCase(UserRepository(db))


@router.post('/', response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_async_db),
    use_case: RegisterUserUseCase = Depends(get_register_use_case),
):
    try:
        created_user = await use_case.execute(user.email, user.password)
        await db.commit()
        return created_user
    except EmailAlreadyRegisteredError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email already registered')


@router.post('/token')
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    use_case: LoginUseCase = Depends(get_login_use_case),
):
    try:
        return await use_case.execute(form_data.username, form_data.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post('/refresh-token')
async def refresh_token(
    body: RefreshTokenRequest,
    use_case: RefreshTokenUseCase = Depends(get_refresh_use_case),
):
    try:
        return await use_case.execute(body.refresh_token)
    except (InvalidCredentialsError, jwt.PyJWTError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post('/access-token')
async def get_new_access_token(
    body: RefreshTokenRequest,
    use_case: GetNewAccessTokenUseCase = Depends(get_new_access_token_use_case),
):
    try:
        return await use_case.execute(body.refresh_token)
    except (InvalidCredentialsError, jwt.PyJWTError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )