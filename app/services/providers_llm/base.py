from abc import ABC, abstractmethod


class LLMProvider(ABC):

    @abstractmethod
    async def generate(self, prompt: str,
                       temperature:
                       float = 0.7) -> str:
        pass

class AIProviderError(Exception):
    pass