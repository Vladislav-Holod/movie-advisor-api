import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.infrastructure.database.session import get_async_db
from app.infrastructure.database.repositories.user_repository import UserRepository

oauth_scheme = OAuth2PasswordBearer(tokenUrl='/user/token')


async def get_current_user(
    token: str = Depends(oauth_scheme),
    db: AsyncSession = Depends(get_async_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.decode_token(token)
        email: str | None = payload.get('sub')
        token_type: str | None = payload.get('token_type')
        if email is None or token_type != 'access':
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise credentials_exception

    repo = UserRepository(db)
    user = await repo.get_active_by_email(email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')
    return user