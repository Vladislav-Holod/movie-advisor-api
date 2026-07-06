import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from loguru import logger


class Settings(BaseSettings):
    AI_API_KEY: str
    MODEL_NAME: str = "gemini-2.5-flash"
    ALGORITHM: str = 'HS256'
    SECRET_KEY: str
    API_POISKINO_KEY: str
    APP_VERSION: str
    DATABASE_URL: str = "sqlite+aiosqlite:///./moviebase.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()

# @lru_cache()
# def get_settings() -> Settings:
# logger.info('Загрузка настроек...')
# return Settings()
