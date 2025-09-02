"""
Модель дня рождения
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Birthday:
    id: int
    user_id: int
    full_name: str
    day: int
    month: int
    year: Optional[int]
    description: Optional[str] = None
    created_at: Optional[str] = None

