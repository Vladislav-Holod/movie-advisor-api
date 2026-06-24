import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.schemas import UserCreate, User, RefreshTokenRequest
from db_depends import get_async_db
from app.models import UserModel, UserProfileModel
from auth import (hash_password,
                  verify_password,
                  create_access_token,
                  create_refresh_token)
from auth import SECRET_KEY, ALGORITHM

router = APIRouter(
    prefix='/user',
    tags=['user_auth']
)


# ADD ROTATION REFRESH TOKEEEEN
# Нужно обьединить /refresh tokens в один эндпонит
# настроить хранение в бд и проверять токены какие надо обновлять какие нет
# -----------------------------

@router.post('/', response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate,
                      db: AsyncSession = Depends(get_async_db)):
    """
    Register new users
    """
    email_register = await db.scalars(select(UserModel).where(UserModel.email == user.email))
    if email_register.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='Email already registered')

    db_user = UserModel(
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    db.add(db_user)
    await db.flush()
    db_profile = UserProfileModel(
        user_id=db_user.id
    )
    db.add(db_profile)
    await db.commit()

    return db_user


@router.post('/token')
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_async_db)):
    """
    It authenticates the user and returns a JWT with email, role, and id.
    """
    stmt_users = await db.scalars(
        select(UserModel).where(UserModel.email == form_data.username, UserModel.is_active == True)
    )
    user = stmt_users.first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token = create_access_token(data={'sub': user.email,
                                             'id': user.id})
    refresh_token = create_refresh_token(data={'sub': user.email,
                                               'id': user.id})
    return {'access_token': access_token,
            'refresh_token': refresh_token, 'token_type': 'bearer'}


@router.post('/refresh-token')
async def refresh_token(
        body: RefreshTokenRequest,
        db: AsyncSession = Depends(get_async_db),
):
    """
    Update refresh tokens, aссepts old refresh tokens in body request
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    old_refresh_token = body.refresh_token
    try:
        payload = jwt.decode(old_refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get('sub')
        token_type: str | None = payload.get('token_type')

        if email is None or token_type != 'refresh':
            raise credentials_exception

    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    result = await db.scalars(select(UserModel).where(UserModel.email == email,
                                                      UserModel.is_active == True))
    user = result.first()
    if user is None:
        raise credentials_exception

    new_refresh_token = create_refresh_token(
        data={'sub': user.email, 'id': user.id}
    )
    new_access_token = create_access_token(
        data={'sub': email, 'id': user.id}
    )

    return {'access_token': new_access_token,
            'refresh_token': new_refresh_token, 'token_type': 'bearer'}


@router.post('/access-token')
async def get_new_access_token(
        body: RefreshTokenRequest,
        db: AsyncSession = Depends(get_async_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    refresh_toke = body.refresh_token
    try:
        payload = jwt.decode(refresh_toke, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get('sub')
        token_type: str | None = payload.get('token_type')

        if email is None or token_type != 'refresh':
            raise credentials_exception

    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    stmt_user = select(UserModel).where(UserModel.email == email,
                                        UserModel.is_active == True)
    user = (await db.scalars(stmt_user)).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token = create_access_token(data={'sub': email, 'id': user.id})
    return {
        "access-token": access_token, 'token_type': 'bearer'
    }
