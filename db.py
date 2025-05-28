import os
from dotenv import load_dotenv
load_dotenv()
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

# Создание всех таблиц
def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Пользователи
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    first_name TEXT,
                    username TEXT,
                    registered_at TEXT,
                    theme TEXT DEFAULT 'auto'
                );
            """)

            # Покупки
            cur.execute("""
                CREATE TABLE IF NOT EXISTS shopping (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    item TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    status TEXT DEFAULT 'Нужно купить',
                    created_at TEXT
                );
            """)

            # Мероприятия
            cur.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    location TEXT NOT NULL,
                    start_at TEXT NOT NULL,
                    end_at TEXT NOT NULL,
                    active BOOLEAN DEFAULT TRUE,
                    created_at TEXT
                );
            """)

            # Логи
            cur.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id SERIAL PRIMARY KEY,
                    type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TEXT
                );
            """)

            # Логи отправленных напоминаний
            cur.execute("""
                CREATE TABLE IF NOT EXISTS reminder_logs (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    event_id INTEGER NOT NULL,
                    sent_at TEXT
                );
            """)

            # Задачи
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    due_date TEXT,
                    priority TEXT DEFAULT 'обычная',
                    completed BOOLEAN DEFAULT FALSE,
                    created_at TEXT
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id BIGINT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT,
                    PRIMARY KEY (user_id, key)
                );
            """)

            conn.commit()

# ✅ Пользователи
def add_user(user_id: int, first_name: str, username: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (user_id, first_name, username, registered_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id) DO NOTHING;
            """, (user_id, first_name, username, datetime.utcnow().isoformat()))
            conn.commit()

# Универсальная функция для обновления любой настройки пользователя
def update_user_setting(user_id: int, key: str, value: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO user_settings (user_id, key, value)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, key) DO UPDATE SET value = EXCLUDED.value
            """, (user_id, key, value))
            conn.commit()

# Универсальная функция для получения всех настроек пользователя
def get_user_settings(user_id: int) -> dict:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT key, value FROM user_settings WHERE user_id = %s
            """, (user_id,))
            rows = cur.fetchall()
            return {row["key"]: row["value"] for row in rows}

# Получить конкретную настройку пользователя по ключу
def get_user_setting(user_id: int, key: str) -> str:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT value FROM user_settings
                WHERE user_id = %s AND key = %s
            """, (user_id, key))
            row = cur.fetchone()
            return row["value"] if row else None

# ✅ Покупки
def add_purchase(user_id: int, item: str, quantity: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO shopping (user_id, item, quantity, status, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, item, quantity, 'Нужно купить', datetime.utcnow().isoformat()))
            conn.commit()

def get_purchases_by_status(status: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            if status == "Все":
                cur.execute("""
                    SELECT id, item, quantity, status, created_at
                    FROM shopping
                    ORDER BY created_at DESC
                """)
            else:
                cur.execute("""
                    SELECT id, item, quantity, status, created_at
                    FROM shopping
                    WHERE status = %s
                    ORDER BY created_at DESC
                """, (status,))
            return cur.fetchall()


# Получить последние покупки пользователя
def get_recent_purchases(user_id: int, limit: int = 5):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, item, quantity, status, created_at
                FROM shopping
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (user_id, limit))
            return cur.fetchall()


def update_purchase_status(purchase_id: int, new_status: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE shopping SET status = %s WHERE id = %s
            """, (new_status, purchase_id))
            conn.commit()

# ✅ Мероприятия
def add_event(title: str, location: str, start_at: str, end_at: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO events (title, location, start_at, end_at, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (title, location, start_at, end_at, datetime.utcnow().isoformat()))
            conn.commit()

def update_event(event_id: int, title: str, location: str, start_at: str, end_at: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE events
                SET title = %s,
                    location = %s,
                    start_at = %s,
                    end_at = %s
                WHERE id = %s
            """, (title, location, start_at, end_at, event_id))
            conn.commit()

def deactivate_event(event_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE events
                SET active = FALSE
                WHERE id = %s
            """, (event_id,))
            conn.commit()

def get_events_by_filter(filter: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            now = datetime.utcnow().isoformat()

            if filter == "Все":
                cur.execute("""
                    SELECT id, title, location, start_at, end_at, active
                    FROM events
                    WHERE active = TRUE OR active = FALSE
                    ORDER BY start_at ASC
                """)
            elif filter == "Прошедшие":
                cur.execute("""
                    SELECT id, title, location, start_at, end_at, active
                    FROM events
                    WHERE active = TRUE AND end_at < %s
                    ORDER BY start_at ASC
                """, (now,))
            else:  # Активные
                cur.execute("""
                    SELECT id, title, location, start_at, end_at, active
                    FROM events
                    WHERE active = TRUE AND end_at >= %s
                    ORDER BY start_at ASC
                """, (now,))

            return cur.fetchall()

def get_today_events():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, location, start_at, end_at, active
                FROM events
                WHERE start_at::date = CURRENT_DATE
                ORDER BY start_at ASC
            """)
            return cur.fetchall()

def log_event(type: str, message: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO logs (type, message, created_at)
                VALUES (%s, %s, %s)
            """, (type, message, datetime.utcnow().isoformat()))
            conn.commit()


# --- Напоминания ---
def has_reminder_been_sent(user_id: int, event_id: int) -> bool:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 1 FROM reminder_logs
                WHERE user_id = %s AND event_id = %s
                LIMIT 1;
            """, (user_id, event_id))
            return cur.fetchone() is not None

def record_reminder_sent(user_id: int, event_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO reminder_logs (user_id, event_id, sent_at)
                VALUES (%s, %s, %s)
            """, (user_id, event_id, datetime.utcnow().isoformat()))
            conn.commit()

# --- Задачи ---
def add_task(user_id: int, title: str, due_date: str, priority: str, description: str = ""):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tasks (user_id, title, description, due_date, priority, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, title, description, due_date, priority, datetime.utcnow().isoformat()))
            conn.commit()

def get_tasks(user_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, description, due_date, priority, completed, created_at
                FROM tasks
                WHERE user_id = %s
                ORDER BY
                    completed ASC,
                    due_date IS NULL, due_date ASC,
                    CASE WHEN priority = 'важная' THEN 0 ELSE 1 END
            """, (user_id,))
            return cur.fetchall()

def get_today_tasks(user_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, description, due_date, priority, completed, created_at
                FROM tasks
                WHERE user_id = %s
                  AND completed = FALSE
                  AND due_date IS NOT NULL
                  AND (
                      due_date::date = CURRENT_DATE
                      OR (
                          due_date::timestamp < CURRENT_TIMESTAMP
                          AND due_date::date = CURRENT_DATE
                      )
                  )
                ORDER BY
                    due_date IS NULL,
                    due_date ASC,
                    CASE WHEN priority = 'важная' THEN 0 ELSE 1 END
            """, (user_id,))
            return cur.fetchall()

def complete_task(task_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE tasks SET completed = TRUE WHERE id = %s
            """, (task_id,))
            conn.commit()

def delete_task(task_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            conn.commit()

def update_task(task_id: int, title: str, description: str, due_date: str, priority: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE tasks
                SET title = %s,
                    description = %s,
                    due_date = %s,
                    priority = %s
                WHERE id = %s
            """, (title, description, due_date, priority, task_id))
            conn.commit()
__all__ = [
    "init_db",
    "add_user",
    "update_user_setting",
    "get_user_settings",
    "get_user_setting",
    "add_purchase",
    "get_purchases_by_status",
    "update_purchase_status",
    "add_event",
    "update_event",
    "deactivate_event",
    "get_events_by_filter",
    "get_today_events",
    "log_event",
    "has_reminder_been_sent",
    "record_reminder_sent",
    "add_task",
    "get_tasks",
    "get_today_tasks",
    "complete_task",
    "delete_task",
    "update_task",
    "get_recent_purchases",
]