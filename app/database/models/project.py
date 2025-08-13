"""
Модели проектов
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Project:
    """Модель проекта"""
    id: Optional[int] = None
    name: str = ""
    owner_id: int = None
    color: str = "#6366f1"
    created_at: Optional[str] = None
    active: bool = True

@dataclass
class ProjectMember:
    """Модель участника проекта"""
    project_id: int
    user_id: int
    joined_at: Optional[str] = None