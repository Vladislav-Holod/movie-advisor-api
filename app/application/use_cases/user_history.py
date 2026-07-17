import uuid

from app.domain.entities.user_history import UserHistory, TaskStatus
from app.domain.repositories.user_history_repository import AbstractUserHistoryRepository


class HistoryNotFoundError(Exception): ...


class CreateHistoryUseCase:
    def __init__(self, history_repo: AbstractUserHistoryRepository):
        self.history_repo = history_repo

    async def execute(self, user_id: int, prompt: str) -> UserHistory:
        task_id = str(uuid.uuid4())
        history = UserHistory(
            id=None,
            task_id=task_id,
            prompt=prompt,
            response='',
            status=TaskStatus.PENDING,
            user_id=user_id,
        )
        return await self.history_repo.create(history)


class GetTaskStatusUseCase:
    def __init__(self, history_repo: AbstractUserHistoryRepository):
        self.history_repo = history_repo

    async def execute(self, task_id: str, user_id: int) -> UserHistory:
        history = await self.history_repo.get_by_task_id(task_id, user_id)
        if history is None:
            raise HistoryNotFoundError()
        return history


class GetHistoryListUseCase:
    def __init__(self, history_repo: AbstractUserHistoryRepository):
        self.history_repo = history_repo

    async def execute(self, user_id: int, cursor: int | None, limit: int):
        items, has_more = await self.history_repo.list_with_recommendations(user_id, cursor, limit)
        next_cursor = items[-1].id if has_more and items else None
        return items, next_cursor, has_more


class GetHistoryByIdUseCase:
    def __init__(self, history_repo: AbstractUserHistoryRepository):
        self.history_repo = history_repo

    async def execute(self, history_id: int, user_id: int) -> UserHistory:
        history = await self.history_repo.get_by_id(history_id, user_id)
        if history is None:
            raise HistoryNotFoundError()
        return history