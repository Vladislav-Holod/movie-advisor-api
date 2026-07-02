from sqlalchemy import Boolean, Integer, String, Text, ForeignKey, DateTime, func,Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from datetime import datetime
from app.models.association_tables import history_movie
import enum

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"

class UserHistoryPrompt(Base):
    __tablename__ = 'user_history'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prompt: Mapped[str] = mapped_column(Text)
    response: Mapped[str] = mapped_column(Text)
    task_id:Mapped[str] = mapped_column(String, unique=True,index=True)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus),
                                                default=TaskStatus.PENDING,
                                                nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'),
                                         nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 server_default=func.now(),
                                                 nullable=False,
                                                 )
    movie_recommend = relationship(
        "MovieModel",
        secondary=history_movie,
        back_populates="prompt_history"
    )
