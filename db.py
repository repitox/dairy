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

            # Проекты
            cur.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    owner_id BIGINT NOT NULL REFERENCES users(user_id),
                    color TEXT,
                    created_at TEXT
                );
            """)

            # Покупки
            cur.execute("""
                CREATE TABLE IF NOT EXISTS shopping (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    project_id INTEGER REFERENCES projects(id),
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
                    user_id BIGINT,
                    project_id INTEGER REFERENCES projects(id),
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
                    project_id INTEGER REFERENCES projects(id),
                    title TEXT NOT NULL,
                    description TEXT,
                    due_date TEXT,
                    priority TEXT DEFAULT 'обычная',
                    completed BOOLEAN DEFAULT FALSE,
                    created_at TEXT
                );
            """)

            # Участники проекта
            cur.execute("""
                CREATE TABLE IF NOT EXISTS project_members (
                    id SERIAL PRIMARY KEY,
                    project_id INTEGER REFERENCES projects(id),
                    user_id BIGINT NOT NULL,
                    joined_at TEXT,
                    UNIQUE (project_id, user_id)
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
    print(f"🗄 Добавляем пользователя: {user_id}, {first_name}, {username}")
    with get_conn() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("""
                    INSERT INTO users (user_id, first_name, username, registered_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (user_id) DO NOTHING;
                """, (user_id, first_name, username, datetime.utcnow().isoformat()))
                conn.commit()
                print("✅ Пользователь добавлен (или уже существует)")
            except Exception as e:
                print("❌ Ошибка при добавлении пользователя:", e)

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
def add_purchase(user_id: int, project_id: int, item: str, quantity: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO shopping (user_id, project_id, item, quantity, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, project_id, item, quantity, 'Нужно купить', datetime.utcnow().isoformat()))
            conn.commit()

def get_purchases_by_status(status: str, project_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            if status == "Все":
                cur.execute("""
                    SELECT id, item, quantity, status, created_at
                    FROM shopping
                    WHERE project_id = %s
                    ORDER BY created_at DESC
                """, (project_id,))
            else:
                cur.execute("""
                    SELECT id, item, quantity, status, created_at
                    FROM shopping
                    WHERE status = %s AND project_id = %s
                    ORDER BY created_at DESC
                """, (status, project_id))
            return cur.fetchall()


# Получить последние покупки пользователя по проекту
def get_recent_purchases(user_id: int, limit: int = 5):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, item, quantity, status, created_at
                FROM shopping
                WHERE status = 'Нужно купить'
                  AND (
                      (user_id = %s AND project_id IS NULL)
                      OR project_id IN (
                          SELECT project_id FROM project_members WHERE user_id = %s
                      )
                  )
                ORDER BY created_at DESC
                LIMIT %s
            """, (user_id, user_id, limit))
            return cur.fetchall()


def update_purchase_status(purchase_id: int, new_status: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE shopping SET status = %s WHERE id = %s
            """, (new_status, purchase_id))
            conn.commit()

# ✅ Мероприятия
def add_event(user_id: int, project_id: int, title: str, location: str, start_at: str, end_at: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO events (user_id, project_id, title, location, start_at, end_at, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (user_id, project_id, title, location, start_at, end_at, datetime.utcnow().isoformat()))
            conn.commit()

def update_event(event_id: int, user_id: int, title: str, location: str, start_at: str, end_at: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE events
                SET user_id = %s,
                    title = %s,
                    location = %s,
                    start_at = %s,
                    end_at = %s
                WHERE id = %s
            """, (user_id, title, location, start_at, end_at, event_id))
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

def get_events_by_filter(user_id: int, filter: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            now = datetime.utcnow().isoformat()

            if filter == "Все":
                cur.execute("""
                    SELECT id, title, location, start_at, end_at, active
                    FROM events
                    WHERE (user_id = %s AND project_id IS NULL)
                       OR project_id IN (
                           SELECT project_id FROM project_members WHERE user_id = %s
                       )
                    ORDER BY start_at ASC
                """, (user_id, user_id))
            elif filter == "Прошедшие":
                cur.execute("""
                    SELECT id, title, location, start_at, end_at, active
                    FROM events
                    WHERE active = TRUE AND end_at < %s
                      AND (
                        (user_id = %s AND project_id IS NULL)
                        OR project_id IN (
                            SELECT project_id FROM project_members WHERE user_id = %s
                        )
                      )
                    ORDER BY start_at ASC
                """, (now, user_id, user_id))
            else:
                cur.execute("""
                    SELECT id, title, location, start_at, end_at, active
                    FROM events
                    WHERE active = TRUE AND end_at >= %s
                      AND (
                        (user_id = %s AND project_id IS NULL)
                        OR project_id IN (
                            SELECT project_id FROM project_members WHERE user_id = %s
                        )
                      )
                    ORDER BY start_at ASC
                """, (now, user_id, user_id))

            return cur.fetchall()

def get_today_events(user_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, location, start_at, end_at, active
                FROM events
                WHERE active = TRUE
                  AND to_timestamp(start_at, 'YYYY-MM-DD"T"HH24:MI:SS"Z"')::date = CURRENT_DATE
                  AND (
                      (user_id = %s AND project_id IS NULL)
                      OR project_id IN (
                          SELECT project_id FROM project_members WHERE user_id = %s
                      )
                  )
                ORDER BY start_at ASC
            """, (user_id, user_id))
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
def add_task(user_id: int, project_id: int, title: str, due_date: str, priority: str, description: str = ""):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tasks (user_id, project_id, title, description, due_date, priority, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (user_id, project_id, title, description, due_date, priority, datetime.utcnow().isoformat()))
            conn.commit()

from typing import Optional

def get_tasks(user_id: int, project_id: Optional[int] = None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            if project_id is not None:
                cur.execute("""
                    SELECT t.id, t.title, t.description, t.due_date, t.priority,
                           t.completed, t.created_at, t.project_id, p.name AS project_name, p.color AS project_color
                    FROM tasks t
                    LEFT JOIN projects p ON t.project_id = p.id
                    WHERE t.project_id = %s
                    ORDER BY
                        t.completed ASC,
                        t.due_date IS NULL, t.due_date ASC,
                        CASE WHEN t.priority = 'важная' THEN 0 ELSE 1 END
                """, (project_id,))
            else:
                cur.execute("""
                    SELECT t.id, t.title, t.description, t.due_date, t.priority,
                           t.completed, t.created_at, t.project_id, p.name AS project_name, p.color AS project_color
                    FROM tasks t
                    LEFT JOIN projects p ON t.project_id = p.id
                    WHERE (t.user_id = %s AND t.project_id IS NULL)
                       OR t.project_id IN (
                           SELECT project_id FROM project_members WHERE user_id = %s
                       )
                    ORDER BY
                        t.completed ASC,
                        t.due_date IS NULL, t.due_date ASC,
                        CASE WHEN t.priority = 'важная' THEN 0 ELSE 1 END
                """, (user_id, user_id))
            return cur.fetchall()

def get_today_tasks(user_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Просроченные задачи
            cur.execute("""
                SELECT tasks.id, tasks.title, tasks.description, tasks.due_date, tasks.priority,
                       tasks.completed, tasks.created_at, tasks.project_id,
                       projects.name AS project_name, projects.color AS project_color
                FROM tasks
                LEFT JOIN projects ON tasks.project_id = projects.id
                WHERE tasks.completed = FALSE
                  AND tasks.due_date IS NOT NULL
                  AND tasks.due_date::timestamp < CURRENT_TIMESTAMP
                  AND (
                      (tasks.user_id = %s AND tasks.project_id IS NULL)
                      OR tasks.project_id IN (
                          SELECT project_id FROM project_members WHERE user_id = %s
                      )
                  )
                ORDER BY
                    tasks.due_date ASC,
                    CASE WHEN tasks.priority = 'важная' THEN 0 ELSE 1 END
            """, (user_id, user_id))
            overdue = cur.fetchall()

            # Задачи на сегодня
            cur.execute("""
                SELECT tasks.id, tasks.title, tasks.description, tasks.due_date, tasks.priority,
                       tasks.completed, tasks.created_at, tasks.project_id,
                       projects.name AS project_name, projects.color AS project_color
                FROM tasks
                LEFT JOIN projects ON tasks.project_id = projects.id
                WHERE tasks.completed = FALSE
                  AND (
                      tasks.due_date::date = CURRENT_DATE
                      AND (tasks.due_date::timestamp >= CURRENT_TIMESTAMP OR tasks.due_date ~ '^\d{4}-\d{2}-\d{2}$')
                  )
                  AND (
                      (tasks.user_id = %s AND tasks.project_id IS NULL)
                      OR tasks.project_id IN (
                          SELECT project_id FROM project_members WHERE user_id = %s
                      )
                  )
                ORDER BY
                    tasks.due_date IS NULL,
                    tasks.due_date ASC,
                    CASE WHEN tasks.priority = 'важная' THEN 0 ELSE 1 END
            """, (user_id, user_id))
            today = cur.fetchall()

            return {"overdue": overdue, "today": today}

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

# --- Проекты ---
def create_project(name: str, owner_id: int, color: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO projects (name, owner_id, color, created_at)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
            """, (name, owner_id, color, datetime.utcnow().isoformat()))
            project_id = cur.fetchone()["id"]
            conn.commit()
            add_project_member(project_id, owner_id)
            return project_id

# --- Участники проекта ---
def add_project_member(project_id: int, user_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO project_members (project_id, user_id, joined_at)
                VALUES (%s, %s, %s)
                ON CONFLICT (project_id, user_id) DO NOTHING;
            """, (project_id, user_id, datetime.utcnow().isoformat()))
            conn.commit()

def get_project(project_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM projects WHERE id = %s", (project_id,))
            return cur.fetchone()

# --- Получить проекты пользователя ---
def get_user_projects(user_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.id, p.name, p.color
                FROM projects p
                JOIN project_members pm ON p.id = pm.project_id
                WHERE pm.user_id = %s
                ORDER BY p.created_at DESC
            """, (user_id,))
            return cur.fetchall()

# --- Получить мероприятия пользователя (личные и проектные) ---
def get_user_events(user_id: int, filter: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            now = datetime.utcnow().isoformat()

            if filter == "Все":
                cur.execute("""
                    SELECT id, title, location, start_at, end_at, active
                    FROM events
                    WHERE active = TRUE
                      AND (
                          (user_id = %s AND project_id IS NULL)
                          OR project_id IN (
                              SELECT project_id FROM project_members WHERE user_id = %s
                          )
                      )
                    ORDER BY start_at ASC
                """, (user_id, user_id))
            elif filter == "Прошедшие":
                cur.execute("""
                    SELECT id, title, location, start_at, end_at, active
                    FROM events
                    WHERE active = TRUE AND end_at < %s
                      AND (
                          (user_id = %s AND project_id IS NULL)
                          OR project_id IN (
                              SELECT project_id FROM project_members WHERE user_id = %s
                          )
                      )
                    ORDER BY start_at ASC
                """, (now, user_id, user_id))
            else:  # Предстоящие
                cur.execute("""
                    SELECT id, title, location, start_at, end_at, active
                    FROM events
                    WHERE active = TRUE AND end_at >= %s
                      AND (
                          (user_id = %s AND project_id IS NULL)
                          OR project_id IN (
                              SELECT project_id FROM project_members WHERE user_id = %s
                          )
                      )
                    ORDER BY start_at ASC
                """, (now, user_id, user_id))

            rows = cur.fetchall()
            print("EVENTS:", rows)
            return rows

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
    "create_project",
    "add_project_member",
    "get_project",
    "get_user_projects",
    "get_user_events",
]