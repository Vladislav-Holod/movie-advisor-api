from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime


class BookPrompt(BaseModel):
    prompt: str = Field(...,
                        min_length=10,
                        max_length=300,
                        description='Промт для нашей нейросети')


class Book(BaseModel):
    name_book: str = Field(max_length=150, description='Имя книги')
    author: str | None = Field(description='Автор книги')
    image: str | None = Field(description='ссылка на картинку книги')


class RecommendResponse(BaseModel):
    prompt: str
    topic: str
    books: list[Book]


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
    name: str = Field(max_length=80)
    favorite_genres: str | None = Field(description='Любимые жанры')
    about_me: str | None = Field(max_length=300, description='Дополнительная информация о пользователе')
    user_id: int = Field(description='Кому принадлежит профиль')
    created_at: datetime = Field('Время создание профиля')
    model_config = ConfigDict(from_attributes=True)


class UserUpdateProfile(BaseModel):
    name: str = Field(max_length=80)
    favorite_genres: str | None = Field(max_length=200, description='Любимые жанры')
    about_me: str | None = Field(max_length=300, description='Дополнительная информация о пользователе')

