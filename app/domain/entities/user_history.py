from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.domain.entities.movie import Movie


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class UserHistory:
    id: int | None
    task_id: str
    prompt: str
    response: str
    status: TaskStatus
    user_id: int
    created_at: datetime | None = None
    movie_recommend: list[Movie] = field(default_factory=list)