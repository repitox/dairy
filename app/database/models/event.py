"""
Модели событий
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Event:
    """Модель события"""
    id: Optional[int] = None
    user_id: int = None
    project_id: Optional[int] = None
    title: str = ""
    location: str = ""
    start_at: Optional[str] = None
    end_at: Optional[str] = None
    active: bool = True
    created_at: Optional[str] = None
    description: Optional[str] = None