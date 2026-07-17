from app.core.config import settings
from app.domain.services.ai_recommendation_service import AIRecommendationService
from app.infrastructure.external_api.poiskino_provider import PoiskinoProvider
from app.infrastructure.llm.providers.gemeni_provider import GeminiProvider

ai_recommendation_service = AIRecommendationService(GeminiProvider())
poiskino_provider = PoiskinoProvider(api_key=settings.API_POISKINO_KEY)