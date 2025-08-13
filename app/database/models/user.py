"""
Модели пользователей
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class User:
    """Модель пользователя"""
    id: Optional[int] = None
    telegram_id: int = None
    first_name: str = ""
    username: str = ""
    registered_at: Optional[str] = None
    theme: str = "auto"

@dataclass
class UserSetting:
    """Модель настройки пользователя"""
    user_id: int
    key: str
    value: str