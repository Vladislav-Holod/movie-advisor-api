from google import genai
from loguru import logger

from app.core.config import settings
from app.domain.repositories.llm_provider import AbstractLLMProvider, AIProviderError


class GeminiProvider(AbstractLLMProvider):
    def __init__(self):
        self.__api_key = settings.AI_API_KEY
        self.__client = genai.Client(api_key=self.__api_key)

    async def generate(self, prompt: str, temperature: float = 0.7) -> str:
        try:
            result = await self.__client.aio.models.generate_content(
                model=settings.MODEL_NAME,
                contents=prompt,
                config=genai.types.GenerateContentConfig(response_mime_type="application/json"),
            )
        except Exception as e:
            logger.error(f'Ошибка AI - {e}')
            raise AIProviderError(f'Внутренняя ошибка AI {e}')
        return result.text