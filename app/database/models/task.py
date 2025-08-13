"""
Модели задач
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Task:
    """Модель задачи"""
    id: Optional[int] = None
    user_id: int = None
    project_id: Optional[int] = None
    title: str = ""
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: str = "обычная"
    completed: bool = False
    created_at: Optional[str] = None
    completed_at: Optional[str] = None