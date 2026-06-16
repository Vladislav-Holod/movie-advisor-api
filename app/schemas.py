from pydantic import BaseModel, Field


class BookPrompt(BaseModel):
    prompt: str = Field(...,
                        min_length=10,
                        max_length=300,
                        description='Промт для нашей нейросети')


class Book(BookPrompt):
    name_book: str = Field(max_length=150, description='Имя книги')
    genre: str | None = Field(description='Жанр книги')
    image: str = Field(description='ссылка на картинку книги')

class RecommendResponse(BaseModel):
    prompt: str
    books: list[Book]
