from google import genai
from google.genai import types
from .base import LLMProvider, AIProviderError
from app.config import settings
from loguru import logger


class GeminiProvider(LLMProvider):

    def __init__(self):
        self.__api_key = settings.AI_API_KEY
        self.__client = genai.Client(api_key=self.__api_key)

    async def generate(self, prompt: str, temperature: float = 0.7) -> str:
        try:
            result = await self.__client.aio.models.generate_content(
                model=settings.MODEL_NAME,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json")
            )
        except Exception as e:
            logger.error(f'Ошибка AI - {e}')
            raise AIProviderError(f'Внутреняя ошибка AI {e}')
        return result.text