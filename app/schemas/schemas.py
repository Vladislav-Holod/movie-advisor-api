from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime
from typing import List

class MoviePrompt(BaseModel):
    prompt: str = Field(...,
                        min_length=10,
                        max_length=300,
                        description='Промт для нашей нейросети')


class Movie(BaseModel):
    id: int
    id_pois: int | None = None
    name_movie: str = Field(default="Без имени", description="Название фильма")
    year: int | None = Field(default=None, description="Год выпуска")
    genres: List[str] = Field(default_factory=list, description="Жанры фильма")
    description: str = Field(default="empty", description="Описание фильма")
    poster_image: str = Field(
        default="https://avatars.mds.yandex.net/get-kinopoisk-image/1946459/daf5de47-6c50-4d78-a4e1-f2d7028af7c8/300x450",
        description="Ссылка на постер фильма"
    )
    movieLength: int | None = Field(default=None, description="Длительность фильма в минутах")
    rating: float = Field(default=0.0, description="Рейтинг фильма")

    model_config = ConfigDict(from_attributes=True)


class RecommendResponse(BaseModel):
    prompt: str
    title: str
    movies: list[Movie]


class UserCreate(BaseModel):
    email: EmailStr = Field(description='Email пользователя')
    password: str = Field(min_length=8, description='Пароль (минимум 8 символов)')


class User(BaseModel):
    id: int = Field(description='Уникальный идентификатор пользователя')
    email: EmailStr = Field(description='Email пользователя')
    is_active: bool = Field(description='Активность пользователя ')
    model_config = ConfigDict(from_attributes=True)


class RefreshTokenRequest(BaseModel):
    """
    Модель для REFRESH jwt токена
    """
    refresh_token: str = Field('Refresh JWT Tokens')


class UserProfile(BaseModel):
    id: int = Field(description='Уникальный идентификатор пользователя')
    name: str | None = Field(default=None, max_length=80)
    favorite_genres: str | None = Field(description='Любимые жанры')
    about_me: str | None = Field(max_length=300, description='Дополнительная информация о пользователе')
    user_id: int = Field(description='Кому принадлежит профиль')
    created_at: datetime = Field('Время создание профиля')
    model_config = ConfigDict(from_attributes=True)


class UserUpdateProfile(BaseModel):
    name: str | None = Field(default=None, max_length=80)
    favorite_genres: str | None = Field(default=None, max_length=200, description='Любимые жанры')
    about_me: str | None = Field(default=None, max_length=300, description='Дополнительная информация о пользователе')