"""
Модели покупок
"""
from dataclasses import dataclass
from typing import Optional
from decimal import Decimal

@dataclass
class Purchase:
    """Модель покупки"""
    id: Optional[int] = None
    user_id: int = None
    project_id: Optional[int] = None
    name: str = ""
    quantity: int = 1
    price: Optional[Decimal] = None
    category: str = "other"
    completed: bool = False
    created_at: Optional[str] = None
    shopping_list_id: Optional[int] = None
    url: Optional[str] = None
    comment: Optional[str] = None

@dataclass
class ShoppingList:
    """Модель списка покупок"""
    id: Optional[int] = None
    name: str = ""
    project_id: int = None
    user_id: int = None
    created_at: Optional[str] = None
    active: bool = True