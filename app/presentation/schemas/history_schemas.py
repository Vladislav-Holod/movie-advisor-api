from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.presentation.schemas.movie_schemas import Movie


class UserHistory(BaseModel):
    id: int = Field(description='Уникальный идентификатор одной истории')
    prompt: str = Field(description='Промт')
    response: str = Field(description='Ответ')
    user_id: int = Field(description='id пользователя')
    created_at: datetime = Field(description='Время')
    movie_list: list[Movie] = Field(validation_alias="movie_recommend")

    model_config = ConfigDict(from_attributes=True)


class UserGroupHistory(BaseModel):
    history: list[UserHistory] = Field(description='Список истории')
    next_cursor: int | None = Field(default=None, description='Курсор для следующей страницы')
    has_more: bool = Field(default=False, description='Есть ли еще истории для пагинации')