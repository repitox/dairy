"""
Утилиты для работы с датами и временем с учетом часовых поясов
"""
from datetime import datetime, timedelta
from typing import Optional


def parse_datetime_string(datetime_str: str, user_timezone_offset: str) -> Optional[datetime]:
    """
    Парсит строку даты/времени из пользовательского часового пояса и конвертирует в UTC
    
    Args:
        datetime_str: Строка даты в формате ISO (например, "2024-01-15T14:30")
        user_timezone_offset: Смещение часового пояса пользователя в часах (например, "+3" или "-5")
    
    Returns:
        datetime объект в UTC или None при ошибке
    """
    if not datetime_str:
        return None
    
    try:
        # Парсим дату
        if 'T' in datetime_str:
            user_datetime = datetime.fromisoformat(datetime_str.replace('Z', ''))
        else:
            # Если только дата, добавляем время 00:00
            user_datetime = datetime.fromisoformat(f"{datetime_str}T00:00:00")
        
        # Получаем смещение часового пояса
        try:
            offset_hours = int(user_timezone_offset)
        except (ValueError, TypeError):
            offset_hours = 0
        
        # Конвертируем в UTC (вычитаем смещение пользователя)
        utc_datetime = user_datetime - timedelta(hours=offset_hours)
        
        return utc_datetime
        
    except Exception as e:
        print(f"Ошибка парсинга даты '{datetime_str}' с часовым поясом '{user_timezone_offset}': {e}")
        return None


def format_datetime_for_user(utc_datetime: datetime, user_timezone_offset: str, format_type: str = "full") -> str:
    """
    Форматирует UTC дату для отображения пользователю в его часовом поясе
    
    Args:
        utc_datetime: datetime объект в UTC
        user_timezone_offset: Смещение часового пояса пользователя в часах
        format_type: Тип форматирования ("full", "date", "time", "relative")
    
    Returns:
        Отформатированная строка даты
    """
    if not utc_datetime:
        return ""
    
    try:
        # Получаем смещение часового пояса
        try:
            offset_hours = int(user_timezone_offset)
        except (ValueError, TypeError):
            offset_hours = 0
        
        # Конвертируем в пользовательский часовой пояс (добавляем смещение)
        user_datetime = utc_datetime + timedelta(hours=offset_hours)
        
        if format_type == "full":
            return user_datetime.strftime("%d.%m.%Y %H:%M")
        elif format_type == "date":
            return user_datetime.strftime("%d.%m.%Y")
        elif format_type == "time":
            return user_datetime.strftime("%H:%M")
        elif format_type == "relative":
            return get_relative_date_text(user_datetime)
        else:
            return user_datetime.strftime("%d.%m.%Y %H:%M")
            
    except Exception as e:
        print(f"Ошибка форматирования даты {utc_datetime} с часовым поясом {user_timezone_offset}: {e}")
        return str(utc_datetime)


def get_relative_date_text(user_datetime: datetime) -> str:
    """
    Возвращает относительный текст даты (сегодня, завтра, вчера и т.д.)
    
    Args:
        user_datetime: datetime в часовом поясе пользователя
    
    Returns:
        Относительный текст даты
    """
    now = datetime.now()
    
    # Сравниваем только даты, игнорируя время
    date_only = user_datetime.date()
    today = now.date()
    
    diff_days = (date_only - today).days
    
    if diff_days == 0:
        return "Сегодня"
    elif diff_days == 1:
        return "Завтра"
    elif diff_days == -1:
        return "Вчера"
    elif diff_days < -1:
        return f"{abs(diff_days)} дн. назад"
    elif diff_days <= 7:
        return f"Через {diff_days} дн."
    else:
        return user_datetime.strftime("%d.%m")


def is_date_today(utc_datetime: datetime, user_timezone_offset: str) -> bool:
    """
    Проверяет, является ли дата сегодняшней в часовом поясе пользователя
    """
    if not utc_datetime:
        return False
    
    try:
        offset_hours = int(user_timezone_offset)
    except (ValueError, TypeError):
        offset_hours = 0
    
    user_datetime = utc_datetime + timedelta(hours=offset_hours)
    now = datetime.now()
    
    return user_datetime.date() == now.date()


def is_date_overdue(utc_datetime: datetime, user_timezone_offset: str) -> bool:
    """
    Проверяет, является ли дата просроченной в часовом поясе пользователя
    """
    if not utc_datetime:
        return False
    
    try:
        offset_hours = int(user_timezone_offset)
    except (ValueError, TypeError):
        offset_hours = 0
    
    user_datetime = utc_datetime + timedelta(hours=offset_hours)
    now = datetime.now()
    
    return user_datetime < now


def get_user_current_time(user_timezone_offset: str) -> datetime:
    """
    Возвращает текущее время в часовом поясе пользователя
    """
    try:
        offset_hours = int(user_timezone_offset)
    except (ValueError, TypeError):
        offset_hours = 0
    
    utc_now = datetime.utcnow()
    return utc_now + timedelta(hours=offset_hours)


def convert_datetime_local_to_utc(datetime_local_str: str, user_timezone_offset: str) -> Optional[str]:
    """
    Конвертирует значение из datetime-local input в UTC ISO строку
    
    Args:
        datetime_local_str: Строка из datetime-local input (например, "2024-01-15T14:30")
        user_timezone_offset: Смещение часового пояса пользователя
    
    Returns:
        UTC ISO строка или None при ошибке
    """
    utc_datetime = parse_datetime_string(datetime_local_str, user_timezone_offset)
    return utc_datetime.isoformat() if utc_datetime else None


def convert_utc_to_datetime_local(utc_iso_str: str, user_timezone_offset: str) -> Optional[str]:
    """
    Конвертирует UTC ISO строку в формат для datetime-local input
    
    Args:
        utc_iso_str: UTC ISO строка
        user_timezone_offset: Смещение часового пояса пользователя
    
    Returns:
        Строка в формате datetime-local или None при ошибке
    """
    if not utc_iso_str:
        return None
    
    try:
        utc_datetime = datetime.fromisoformat(utc_iso_str.replace('Z', ''))
        
        try:
            offset_hours = int(user_timezone_offset)
        except (ValueError, TypeError):
            offset_hours = 0
        
        user_datetime = utc_datetime + timedelta(hours=offset_hours)
        
        # Форматируем для datetime-local (YYYY-MM-DDTHH:MM)
        return user_datetime.strftime("%Y-%m-%dT%H:%M")
        
    except Exception as e:
        print(f"Ошибка конвертации UTC '{utc_iso_str}' в datetime-local: {e}")
        return None