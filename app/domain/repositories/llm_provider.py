from abc import ABC, abstractmethod


class AbstractLLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, temperature: float = 0.7) -> str: ...


class AIProviderError(Exception):
    pass