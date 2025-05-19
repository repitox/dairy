import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Подключение к базе из переменной окружения
DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

# ✅ Создание таблиц
def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Пользователи
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    first_name TEXT,
                    username TEXT,
                    registered_at TEXT
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
            conn.commit()

# ✅ Добавить пользователя
def add_user(user_id: int, first_name: str, username: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (user_id, first_name, username, registered_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id) DO NOTHING;
            """, (user_id, first_name, username, datetime.utcnow().isoformat()))
            conn.commit()

# ✅ Добавить покупку
def add_purchase(user_id: int, item: str, quantity: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO shopping (user_id, item, quantity, status, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, item, quantity, 'Нужно купить', datetime.utcnow().isoformat()))
            conn.commit()

# ✅ Получить покупки по статусу
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

# ✅ Обновить статус покупки
def update_purchase_status(purchase_id: int, new_status: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE shopping SET status = %s WHERE id = %s
            """, (new_status, purchase_id))
            conn.commit()

# ✅ Получить всех пользователей
def get_all_users():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT user_id, first_name, username, registered_at
                FROM users
                ORDER BY registered_at DESC
            """)
            return cur.fetchall()
        
# ✅ МЕРОПРИЯТИЯ

def add_event(title: str, location: str, start_at: str, end_at: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO events (title, location, start_at, end_at, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (title, location, start_at, end_at, datetime.utcnow().isoformat()))
            conn.commit()

def get_active_events():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, location, start_at, end_at
                FROM events
                WHERE active = TRUE AND end_at > %s
                ORDER BY start_at ASC
            """, (datetime.utcnow().isoformat(),))
            return cur.fetchall()

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