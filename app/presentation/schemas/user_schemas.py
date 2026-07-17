from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr = Field(description='Email пользователя')
    password: str = Field(min_length=8, description='Пароль (минимум 8 символов)')


class User(BaseModel):
    id: int = Field(description='Уникальный идентификатор пользователя')
    email: EmailStr = Field(description='Email пользователя')
    is_active: bool = Field(description='Активность пользователя')

    model_config = ConfigDict(from_attributes=True)


class UserProfile(BaseModel):
    id: int = Field(description='Уникальный идентификатор профиля')
    name: str | None = Field(default=None, max_length=80)
    favorite_genres: str | None = Field(default=None, description='Любимые жанры')
    about_me: str | None = Field(default=None, max_length=300, description='Дополнительная информация о пользователе')
    user_id: int = Field(description='Кому принадлежит профиль')
    created_at: "datetime" = Field(description='Время создания профиля')
    image_id: str | None = Field(default=None, description='ID изображения профиля')
    image_url: str | None = Field(default=None, description='URL изображения профиля')

    model_config = ConfigDict(from_attributes=True)


class UserUpdateProfile(BaseModel):
    name: str | None = Field(default=None, max_length=80)
    favorite_genres: str | None = Field(default=None, max_length=200, description='Любимые жанры')
    about_me: str | None = Field(default=None, max_length=300, description='Дополнительная информация о пользователе')


