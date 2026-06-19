from sqlalchemy import Integer, ForeignKey, DateTime, func, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from database import Base


class UserProfileModel(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str | None] = mapped_column(String, unique=True)
    favorite_genres: Mapped[str | None] = mapped_column(String, default=None)
    about_me: Mapped[str | None] = mapped_column(Text, default=None)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"),
                                         unique=True,
                                         nullable=False
                                         )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 server_default=func.now(),
                                                 nullable=False,
                                                 )

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="profile"
    )
