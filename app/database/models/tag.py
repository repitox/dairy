"""
Модели тегов
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Tag:
    """Модель тега"""
    id: Optional[int] = None
    name: str = ""
    background_color: str = "#6366f1"
    project_id: int = None
    created_by_id: int = None
    created_at: Optional[str] = None
    active: bool = True


@dataclass
class TagAssociation:
    """Модель связи тега с объектом (задача, встреча, покупка)"""
    id: Optional[int] = None
    tag_id: int = None
    object_type: str = ""  # 'task', 'event', 'purchase'
    object_id: int = None
    created_at: Optional[str] = None
