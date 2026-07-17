from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserProfile:
    id: int | None
    user_id: int
    name: str | None = None
    favorite_genres: str | None = None
    about_me: str | None = None
    image_id: str | None = None
    created_at: datetime | None = None