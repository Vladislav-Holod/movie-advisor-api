from typing import List

from pydantic import BaseModel, ConfigDict, Field


class MoviePrompt(BaseModel):
    prompt: str = Field(
        ..., min_length=10, max_length=300, description='Промт для нашей нейросети'
    )


class Movie(BaseModel):
    id: int
    id_pois: int | None = None
    name_movie: str = Field(default="Без имени", description="Название фильма")
    year: int | None = Field(default=None, description="Год выпуска")
    genres: List[str] = Field(default_factory=list, description="Жанры фильма")
    description: str | None = Field(default="empty", description="Описание фильма")
    poster_image: str = Field(
        default="https://img.magnific.com/premium-vector/black-blank-book-cover-isolated-transparent_168129-46.jpg?semt=ais_hybrid&w=740",
        description="Ссылка на постер фильма",
    )
    movieLength: int | None = Field(default=None, description="Длительность фильма в минутах")
    rating: float | None = Field(default=0.0, description="Рейтинг фильма")
    reason: str | None = None

    model_config = ConfigDict(from_attributes=True)


class MovieListResponse(BaseModel):
    movies: list[Movie]
    next_cursor: int | None = Field(default=None, description='Курсор для следующей страницы')
    has_more: bool = Field(default=False, description='Есть ли еще фильмы для пагинации')


class RecommendResponse(BaseModel):
    prompt: str
    title: str
    movies: list[Movie]