from dataclasses import dataclass, field


@dataclass
class Movie:
    id: int | None
    name_movie: str
    id_pois: int | None = None
    year: int | None = None
    genres: list[str] = field(default_factory=list)
    description: str = 'empty'
    poster_image: str = ''
    movie_length: int | None = None
    rating: float = 0.0