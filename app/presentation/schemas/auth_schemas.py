from pydantic import BaseModel, Field


class RefreshTokenRequest(BaseModel):
    """Модель для refresh JWT токена."""
    refresh_token: str = Field(description='Refresh JWT Token')