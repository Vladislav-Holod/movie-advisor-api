from abc import ABC, abstractmethod


class AbstractFileStorage(ABC):
    @abstractmethod
    async def save(self, filename: str, content: bytes) -> None: ...

    @abstractmethod
    def delete(self, filename: str) -> None: ...

    @abstractmethod
    def exists(self, filename: str) -> bool: ...