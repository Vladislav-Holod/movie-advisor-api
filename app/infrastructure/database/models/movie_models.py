from sqlalchemy import Integer, String, JSON, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.association_tables import user_profile_liked_movie
from sqlalchemy import ForeignKey
from .association_tables import history_movie

class MovieModel(Base):
    __tablename__ = "movie_base"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_pois: Mapped[int | None] = mapped_column(Integer, unique=True)
    name_movie: Mapped[str] = mapped_column(String, default='Без имени')
    year: Mapped[int | None] = mapped_column(Integer)
    genres: Mapped[list[str]] = mapped_column(JSON, default=list)
    description: Mapped[str] = mapped_column(Text, default='empty')
    poster_image: Mapped[str] = mapped_column(String,
                                              default='https://avatars.mds.yandex.net/get-kinopoisk-image/1946459/daf5de47-6c50-4d78-a4e1-f2d7028af7c8/300x450')
    movieLength: Mapped[int | None] = mapped_column(Integer)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    liked_by_profiles: Mapped[list['UserProfileModel']] = relationship(
        'UserProfileModel',
        secondary=user_profile_liked_movie,
        back_populates='liked_movie'
    )
    prompt_history = relationship(
        "UserHistoryPrompt",
        secondary=history_movie,
        back_populates="movie_recommend"
    )
