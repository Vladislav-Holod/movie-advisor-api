from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from database import async_session_maker


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async db session
    """
    async with async_session_maker() as session:
        yield session
