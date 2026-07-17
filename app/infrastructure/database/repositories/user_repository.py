from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.users import UserModel


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active_by_email(self, email: str) -> UserModel | None:
        result = await self.session.scalars(
            select(UserModel).where(
                UserModel.email == email,
                UserModel.is_active == True,
            )
        )
        return result.first()