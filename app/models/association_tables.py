from sqlalchemy import Table, Column, Integer, ForeignKey
from database import Base

user_favorite_books = Table(
    "user_favorite_books",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("book_id", ForeignKey("books.id"), primary_key=True),
)

user_profile_liked_books = Table(
    "user_profile_liked_books",
    Base.metadata,
    Column("profile_id", ForeignKey("user_profiles.id"), primary_key=True),
    Column("book_id", ForeignKey("books.id"), primary_key=True),
)