"""
Система напоминаний о событиях
"""
import asyncio
from datetime import datetime, timedelta
from telegram import Bot

from app.core.config import settings
from app.database.connection import get_db_cursor
from app.database.repositories.user_repository import user_repository
from app.utils.datetime_utils import format_datetime_for_user


async def reminder_loop():
    """Цикл напоминаний о событиях"""
    while True:
        now = datetime.utcnow()
        check_time = now + timedelta(minutes=60)
        now_iso = now.isoformat()
        check_iso = check_time.isoformat()

        with get_db_cursor() as cur:
            # События, которые стартуют через 60 минут (плюс/минус 1 минута)
            cur.execute("""
                SELECT id, title, location, start_at
                FROM events
                WHERE active = TRUE
                AND start_at BETWEEN %s AND %s
            """, (now_iso, check_iso))
            events = cur.fetchall()

            cur.execute("SELECT telegram_id FROM users")
            users = [u["telegram_id"] for u in cur.fetchall()]

        if not users:
            _log_event("info", "Нет пользователей для отправки уведомлений.")
        if not events:
            _log_event("info", "Нет подходящих событий для напоминания.")

        bot = Bot(token=settings.BOT_TOKEN)

        for event in events:
            for user_id in users:
                if _has_reminder_been_sent(user_id, event["id"]):
                    continue

                # Получаем часовой пояс пользователя
                user_tz_offset = user_repository.get_user_setting(user_id, "timezone") or "0"
                
                # Парсим UTC дату из БД
                try:
                    utc_start = datetime.fromisoformat(event["start_at"].replace('Z', ''))
                    # Форматируем время для пользователя
                    formatted_time = format_datetime_for_user(utc_start, user_tz_offset, "full")
                except Exception as e:
                    print(f"Ошибка форматирования времени события {event['id']} для пользователя {user_id}: {e}")
                    # Fallback к старому способу
                    try:
                        start = datetime.fromisoformat(event["start_at"])
                        offset_hours = int(user_tz_offset) if user_tz_offset.isdigit() or user_tz_offset.startswith('-') else 0
                        user_time = start + timedelta(hours=offset_hours)
                        formatted_time = user_time.strftime("%d.%m.%y %H:%M")
                    except Exception:
                        formatted_time = event["start_at"]

                try:
                    await bot.send_message(
                        chat_id=user_id,
                        text=(
                            f"🔔 Напоминание\n"
                            f"📅 Скоро начнётся мероприятие:\n"
                            f"«{event['title']}»\n"
                            f"🕒 {formatted_time}\n"
                            f"📍 {event['location']}"
                        )
                    )
                    _log_event("reminder", f"Уведомление отправлено пользователю {user_id} о событии '{event['title']}'")
                    _record_reminder_sent(user_id, event["id"])
                except Exception as e:
                    _log_event("error", f"Ошибка при отправке пользователю {user_id}: {type(e).__name__} — {e}")
        
        await asyncio.sleep(60)


def _has_reminder_been_sent(user_id: int, event_id: int) -> bool:
    """Проверить, было ли уже отправлено напоминание"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) as count FROM reminder_logs 
            WHERE user_id = %s AND event_id = %s
        """, (user_id, event_id))
        result = cur.fetchone()
        return result['count'] > 0


def _record_reminder_sent(user_id: int, event_id: int):
    """Записать факт отправки напоминания"""
    with get_db_cursor() as cur:
        cur.execute("""
            INSERT INTO reminder_logs (user_id, event_id, sent_at)
            VALUES (%s, %s, %s)
        """, (user_id, event_id, datetime.utcnow().isoformat()))


def _log_event(event_type: str, message: str):
    """Записать событие в лог"""
    with get_db_cursor() as cur:
        cur.execute("""
            INSERT INTO logs (type, message, created_at)
            VALUES (%s, %s, %s)
        """, (event_type, message, datetime.utcnow().isoformat()))"""
Система напоминаний о событиях
"""
import asyncio
from datetime import datetime, timedelta
from telegram import Bot

from app.core.config import settings
from app.database.connection import get_db_cursor
from app.database.repositories.user_repository import user_repository


async def reminder_loop():
    """Цикл напоминаний о событиях"""
    while True:
        now = datetime.utcnow()
        check_time = now + timedelta(minutes=60)
        now_iso = now.isoformat()
        check_iso = check_time.isoformat()

        with get_db_cursor() as cur:
            # События, которые стартуют через 60 минут (плюс/минус 1 минута)
            cur.execute("""
                SELECT id, title, location, start_at
                FROM events
                WHERE active = TRUE
                AND start_at BETWEEN %s AND %s
            """, (now_iso, check_iso))
            events = cur.fetchall()

            cur.execute("SELECT telegram_id FROM users")
            users = [u["telegram_id"] for u in cur.fetchall()]

        if not users:
            _log_event("info", "Нет пользователей для отправки уведомлений.")
        if not events:
            _log_event("info", "Нет подходящих событий для напоминания.")

        bot = Bot(token=settings.BOT_TOKEN)

        for event in events:
            for user_id in users:
                if _has_reminder_been_sent(user_id, event["id"]):
                    continue

                # Получаем часовой пояс пользователя
                user_tz_offset = user_repository.get_user_setting(user_id, "timezone") or "0"
                
                # Парсим UTC дату из БД
                try:
                    utc_start = datetime.fromisoformat(event["start_at"].replace('Z', ''))
                    # Форматируем время для пользователя
                    formatted_time = format_datetime_for_user(utc_start, user_tz_offset, "full")
                except Exception as e:
                    print(f"Ошибка форматирования времени события {event['id']} для пользователя {user_id}: {e}")
                    # Fallback к старому способу
                    try:
                        start = datetime.fromisoformat(event["start_at"])
                        offset_hours = int(user_tz_offset) if user_tz_offset.isdigit() or user_tz_offset.startswith('-') else 0
                        user_time = start + timedelta(hours=offset_hours)
                        formatted_time = user_time.strftime("%d.%m.%y %H:%M")
                    except Exception:
                        formatted_time = event["start_at"]

                try:
                    await bot.send_message(
                        chat_id=user_id,
                        text=(
                            f"🔔 Напоминание\n"
                            f"📅 Скоро начнётся мероприятие:\n"
                            f"«{event['title']}»\n"
                            f"🕒 {formatted_time}\n"
                            f"📍 {event['location']}"
                        )
                    )
                    _log_event("reminder", f"Уведомление отправлено пользователю {user_id} о событии '{event['title']}'")
                    _record_reminder_sent(user_id, event["id"])
                except Exception as e:
                    _log_event("error", f"Ошибка при отправке пользователю {user_id}: {type(e).__name__} — {e}")
        
        await asyncio.sleep(60)


def _has_reminder_been_sent(user_id: int, event_id: int) -> bool:
    """Проверить, было ли уже отправлено напоминание"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) as count FROM reminder_logs 
            WHERE user_id = %s AND event_id = %s
        """, (user_id, event_id))
        result = cur.fetchone()
        return result['count'] > 0


def _record_reminder_sent(user_id: int, event_id: int):
    """Записать факт отправки напоминания"""
    with get_db_cursor() as cur:
        cur.execute("""
            INSERT INTO reminder_logs (user_id, event_id, sent_at)
            VALUES (%s, %s, %s)
        """, (user_id, event_id, datetime.utcnow().isoformat()))


def _log_event(event_type: str, message: str):
    """Записать событие в лог"""
    with get_db_cursor() as cur:
        cur.execute("""
            INSERT INTO logs (type, message, created_at)
            VALUES (%s, %s, %s)
        """, (event_type, message, datetime.utcnow().isoformat()))