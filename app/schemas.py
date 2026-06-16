from pydantic import BaseModel, Field


class BookPrompt(BaseModel):
    prompt: str = Field(...,
                        min_length=10,
                        max_length=300,
                        description='Промт для нашей нейросети')


class Book(BaseModel):
    name_book: str = Field(max_length=150, description='Имя книги')
    author: str | None = Field(description='Автор книги')
    image: str | None= Field(description='ссылка на картинку книги')

class RecommendResponse(BaseModel):
    prompt: str
    topic : str
    books: list[Book]
