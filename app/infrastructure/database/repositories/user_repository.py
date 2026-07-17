from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.repositories.user_repository import AbstractUserRepository
from app.infrastructure.database.models.users import UserModel


def _to_entity(model: UserModel) -> User:
    return User(
        id=model.id,
        email=model.email,
        hashed_password=model.hashed_password,
        is_active=model.is_active,
    )


class UserRepository(AbstractUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        model = await self.session.get(UserModel, user_id)
        return _to_entity(model) if model else None

    async def get_active_by_email(self, email: str) -> User | None:
        result = await self.session.scalars(
            select(UserModel).where(
                UserModel.email == email,
                UserModel.is_active == True,
            )
        )
        model = result.first()
        return _to_entity(model) if model else None

    async def create(self, user: User) -> User:
        model = UserModel(
            email=user.email,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return _to_entity(model)