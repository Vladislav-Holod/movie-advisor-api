from dataclasses import dataclass


@dataclass
class User:
    id: int | None
    email: str
    hashed_password: str
    is_active: bool = True