from app.services.ai_service import AIService
from app.services.providers_llm.gemeni_provider import GeminiProvider
from app.services.externel_api.poiskino import PoiskinoProvider
from app.config import config
from celery import Celery
ai_client = AIService(GeminiProvider())
api_kinopoisk = PoiskinoProvider(api_key=config.API_POISKINO_KEY)

celery_app = Celery(__name__,
                broker='redis://127.0.0.1:6379/0',
                backend='redis://127.0.0.1:6379/0',
                broker_connection_retry_on_startup=True,
                include=['app.tasks.movie_task'])