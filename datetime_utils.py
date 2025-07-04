"""
Утилиты для работы с датами и часовыми поясами
"""
from datetime import datetime, timezone, timedelta
from typing import Optional, Union
import pytz

def get_user_timezone(timezone_offset: Union[str, int, None]) -> pytz.BaseTzInfo:
    """
    Получить объект часового пояса пользователя
    
    Args:
        timezone_offset: Смещение в часах от UTC (например, "+3", "3", -5)
    
    Returns:
        pytz timezone object
    """
    if timezone_offset is None:
        return pytz.UTC
    
    try:
        # Преобразуем в число
        if isinstance(timezone_offset, str):
            offset = int(timezone_offset.replace('+', ''))
        else:
            offset = int(timezone_offset)
        
        # Создаем timezone с нужным смещением
        if offset == 0:
            return pytz.UTC
        else:
            # Создаем фиксированный timezone
            return timezone(timedelta(hours=offset))
    except (ValueError, TypeError):
        return pytz.UTC

def utc_to_user_timezone(utc_datetime: datetime, user_timezone_offset: Union[str, int, None]) -> datetime:
    """
    Конвертировать UTC время в часовой пояс пользователя
    
    Args:
        utc_datetime: Время в UTC
        user_timezone_offset: Смещение часового пояса пользователя
    
    Returns:
        Время в часовом поясе пользователя
    """
    if utc_datetime.tzinfo is None:
        utc_datetime = utc_datetime.replace(tzinfo=pytz.UTC)
    
    user_tz = get_user_timezone(user_timezone_offset)
    return utc_datetime.astimezone(user_tz)

def user_timezone_to_utc(user_datetime: datetime, user_timezone_offset: Union[str, int, None]) -> datetime:
    """
    Конвертировать время из часового пояса пользователя в UTC
    
    Args:
        user_datetime: Время в часовом поясе пользователя
        user_timezone_offset: Смещение часового пояса пользователя
    
    Returns:
        Время в UTC
    """
    user_tz = get_user_timezone(user_timezone_offset)
    
    if user_datetime.tzinfo is None:
        user_datetime = user_tz.localize(user_datetime)
    
    return user_datetime.astimezone(pytz.UTC)

def parse_datetime_string(date_string: str, user_timezone_offset: Union[str, int, None] = None) -> datetime:
    """
    Парсить строку даты/времени
    
    Args:
        date_string: Строка с датой/временем
        user_timezone_offset: Часовой пояс пользователя (если нужно конвертировать в UTC)
    
    Returns:
        datetime объект
    """
    if not date_string:
        return None
    
    # Пробуем разные форматы
    formats = [
        "%Y-%m-%dT%H:%M:%S",      # 2025-07-02T19:00:00
        "%Y-%m-%dT%H:%M",         # 2025-07-02T19:00
        "%Y-%m-%d %H:%M:%S",      # 2025-07-02 19:00:00
        "%Y-%m-%d %H:%M",         # 2025-07-02 19:00
        "%Y-%m-%d",               # 2025-07-02
    ]
    
    parsed_dt = None
    for fmt in formats:
        try:
            parsed_dt = datetime.strptime(date_string, fmt)
            break
        except ValueError:
            continue
    
    if parsed_dt is None:
        raise ValueError(f"Не удалось распарсить дату: {date_string}")
    
    # Если указан часовой пояс пользователя, конвертируем в UTC
    if user_timezone_offset is not None:
        parsed_dt = user_timezone_to_utc(parsed_dt, user_timezone_offset)
    
    return parsed_dt

def format_datetime_for_user(dt: datetime, user_timezone_offset: Union[str, int, None], 
                           format_type: str = "full") -> str:
    """
    Форматировать datetime для отображения пользователю
    
    Args:
        dt: datetime объект (предполагается UTC)
        user_timezone_offset: Часовой пояс пользователя
        format_type: Тип форматирования ("full", "date", "time", "relative")
    
    Returns:
        Отформатированная строка
    """
    if dt is None:
        return ""
    
    # Конвертируем в часовой пояс пользователя
    user_dt = utc_to_user_timezone(dt, user_timezone_offset)
    
    if format_type == "full":
        return user_dt.strftime("%d.%m.%Y %H:%M")
    elif format_type == "date":
        return user_dt.strftime("%d.%m.%Y")
    elif format_type == "time":
        return user_dt.strftime("%H:%M")
    elif format_type == "relative":
        return get_relative_date_text(user_dt)
    else:
        return user_dt.strftime("%d.%m.%Y %H:%M")

def get_relative_date_text(dt: datetime) -> str:
    """
    Получить относительный текст даты (Сегодня, Завтра, и т.д.)
    
    Args:
        dt: datetime в часовом поясе пользователя
    
    Returns:
        Текст относительной даты
    """
    now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
    
    # Сравниваем только даты, игнорируя время
    dt_date = dt.date()
    now_date = now.date()
    
    diff_days = (dt_date - now_date).days
    
    if diff_days < 0:
        return f"{abs(diff_days)}д назад"
    elif diff_days == 0:
        return "Сегодня"
    elif diff_days == 1:
        return "Завтра"
    elif diff_days <= 7:
        return f"{diff_days}д"
    else:
        return dt.strftime("%d.%m")

def is_same_day(dt1: datetime, dt2: datetime) -> bool:
    """
    Проверить, что две даты в один день
    """
    return dt1.date() == dt2.date()

def is_today(dt: datetime, user_timezone_offset: Union[str, int, None]) -> bool:
    """
    Проверить, что дата сегодня в часовом поясе пользователя
    """
    user_dt = utc_to_user_timezone(dt, user_timezone_offset)
    user_tz = get_user_timezone(user_timezone_offset)
    now_user = datetime.now(user_tz)
    return is_same_day(user_dt, now_user)

def is_tomorrow(dt: datetime, user_timezone_offset: Union[str, int, None]) -> bool:
    """
    Проверить, что дата завтра в часовом поясе пользователя
    """
    user_dt = utc_to_user_timezone(dt, user_timezone_offset)
    user_tz = get_user_timezone(user_timezone_offset)
    now_user = datetime.now(user_tz)
    tomorrow = now_user + timedelta(days=1)
    return is_same_day(user_dt, tomorrow)

def is_overdue(dt: datetime, user_timezone_offset: Union[str, int, None]) -> bool:
    """
    Проверить, что дата просрочена в часовом поясе пользователя
    """
    user_dt = utc_to_user_timezone(dt, user_timezone_offset)
    user_tz = get_user_timezone(user_timezone_offset)
    now_user = datetime.now(user_tz)
    return user_dt < now_user