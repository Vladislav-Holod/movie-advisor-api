from sqlalchemy import Table, Column, ForeignKey
from app.infrastructure.database.session import Base

user_profile_liked_movie = Table(
    "user_profile_liked_movie",
    Base.metadata,
    Column("profile_id", ForeignKey("user_profiles.id"), primary_key=True),
    Column("movie_base_id", ForeignKey("movie_base.id"), primary_key=True),
)
history_movie = Table(
    "history_movie",
    Base.metadata,
    Column("history_id", ForeignKey("user_history.id"), primary_key=True),
    Column("movie_id", ForeignKey("movie_base.id"), primary_key=True),
)