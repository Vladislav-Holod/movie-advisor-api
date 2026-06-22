from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from app.models.association_tables import user_favorite_books,user_profile_liked_books

class BookModel(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String)
    genres: Mapped[str | None] = mapped_column(String)

    image_url: Mapped[str | None] = mapped_column(
        String,
        default="https://ndc.book24.ru/resize/410x590/pim/products/images/b4/3a/0199ecd8-8ed9-79b4-8097-a0086047b43a.jpg"
    )

    fans: Mapped[list["UserModel"]] = relationship(
        "UserModel",
        secondary=user_favorite_books,
        back_populates="favorite_books"
    )
    liked_by_profiles:Mapped[list['UserProfileModel']] = relationship(
        'UserProfileModel',
        secondary=user_profile_liked_books,
        back_populates='liked_books'
    )