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
                    timezone TEXT
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
                    due_date TEXT,
                    priority TEXT DEFAULT 'обычная',
                    completed BOOLEAN DEFAULT FALSE,
                    created_at TEXT
                );
            """)

            conn.commit()

# ✅ Пользователи
def add_user(user_id: int, first_name: str, username: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (user_id, first_name, username, registered_at, timezone)
                VALUES (%s, %s, %s, %s, NULL)
                ON CONFLICT (user_id) DO NOTHING;
            """, (user_id, first_name, username, datetime.utcnow().isoformat()))
            conn.commit()

# Обновить timezone пользователя
def update_user_timezone(user_id: int, timezone: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE users SET timezone = %s WHERE user_id = %s
            """, (timezone, user_id))
            conn.commit()

# Получить timezone пользователя
def get_user_timezone(user_id: int) -> str:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT timezone FROM users WHERE user_id = %s
            """, (user_id,))
            result = cur.fetchone()
            return result["timezone"] if result else None

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
def add_task(user_id: int, title: str, due_date: str, priority: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tasks (user_id, title, due_date, priority, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, title, due_date, priority, datetime.utcnow().isoformat()))
            conn.commit()

def get_tasks(user_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, due_date, priority, completed, created_at
                FROM tasks
                WHERE user_id = %s
                ORDER BY
                    completed ASC,
                    due_date IS NULL, due_date ASC,
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