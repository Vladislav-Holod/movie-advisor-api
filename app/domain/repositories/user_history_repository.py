from abc import ABC, abstractmethod

from app.domain.entities.user_history import UserHistory
from app.domain.entities.user_history import TaskStatus

class AbstractUserHistoryRepository(ABC):
    @abstractmethod
    async def create(self, history: UserHistory) -> UserHistory: ...

    @abstractmethod
    async def get_by_task_id(self, task_id: str, user_id: int) -> UserHistory | None: ...

    @abstractmethod
    async def get_by_id(self, history_id: int, user_id: int) -> UserHistory | None: ...

    @abstractmethod
    async def list_for_user(
        self, user_id: int, cursor: int | None, limit: int
    ) -> tuple[list[UserHistory], bool]: ...

    @abstractmethod
    async def set_status(self, task_id: str, status: TaskStatus) -> None: ...

    @abstractmethod
    async def complete(self, task_id: str, response: str, movie_ids: list[int]) -> None: ...