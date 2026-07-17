from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    AI_API_KEY: str
    MODEL_NAME: str = "gemini-2.5-flash"
    ALGORITHM: str = 'HS256'
    SECRET_KEY: str
    API_POISKINO_KEY: str
    APP_VERSION: str
    DATABASE_URL: str = "sqlite+aiosqlite:///./moviebase.db"
    DEBUG: bool = False

    CELERY_BROKER_URL: str = "redis://127.0.0.1:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://127.0.0.1:6379/0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()