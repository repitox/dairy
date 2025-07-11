import os
from dotenv import load_dotenv
# Загружаем .env только если переменная DATABASE_URL не установлена
if not os.getenv("DATABASE_URL"):
    load_dotenv()
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from datetime_utils import (
    parse_datetime_string, format_datetime_for_user, 
    is_today, is_tomorrow, is_overdue, utc_to_user_timezone
)

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
                    registered_at TEXT
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
                    created_at TEXT,
                    description TEXT
                );
            """)

            # Добавляем поле description в events если его нет
            try:
                cur.execute("ALTER TABLE events ADD COLUMN IF NOT EXISTS description TEXT;")
            except Exception as e:
                print(f"Миграция description для events: {e}")

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
                    created_at TEXT,
                    completed_at TEXT
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

            # Заметки
            cur.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(user_id),
                    title TEXT NOT NULL,
                    content TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                
                # Создаем личный проект для пользователя, если его нет
                cur.execute("""
                    INSERT INTO projects (name, owner_id, color, created_at)
                    SELECT '#личное', %s, '#6366f1', %s
                    WHERE NOT EXISTS (
                        SELECT 1 FROM projects WHERE owner_id = %s AND name = '#личное'
                    );
                """, (user_id, datetime.utcnow().isoformat(), user_id))
                
                conn.commit()
                print("✅ Пользователь добавлен (или уже существует)")
            except Exception as e:
                print("❌ Ошибка при добавлении пользователя:", e)

def get_personal_project_id(user_id: int) -> int:
    """Получить ID личного проекта пользователя"""
    import psycopg2
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT id FROM projects 
            WHERE owner_id = %s AND name = '#личное'
            LIMIT 1;
        """, (user_id,))
        result = cur.fetchone()
        if result:
            return result[0]
        else:
            # Создаем личный проект, если его нет
            cur.execute("""
                INSERT INTO projects (name, owner_id, color, created_at)
                VALUES ('#личное', %s, '#6366f1', %s)
                RETURNING id;
            """, (user_id, datetime.utcnow().isoformat()))
            project_id = cur.fetchone()[0]
            conn.commit()
            return project_id
    finally:
        cur.close()
        conn.close()

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
def add_event(user_id: int, project_id: int, title: str, location: str, start_at: str, end_at: str, description: str = None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO events (user_id, project_id, title, location, start_at, end_at, created_at, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, project_id, title, location, start_at, end_at, datetime.utcnow().isoformat(), description))
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
    """Получить события на сегодня"""
    from datetime import datetime, date
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Получаем все активные события пользователя
            cur.execute("""
                SELECT events.id, events.title, events.location, events.start_at, events.end_at, events.active,
                       projects.name AS project_name, projects.color AS project_color
                FROM events
                LEFT JOIN projects ON events.project_id = projects.id
                WHERE events.active = TRUE
                  AND events.start_at IS NOT NULL
                  AND (
                      (events.user_id = %s AND events.project_id IS NULL)
                      OR events.project_id IN (
                          SELECT project_id FROM project_members WHERE user_id = %s
                      )
                  )
                ORDER BY events.start_at ASC
            """, (user_id, user_id))
            all_events = cur.fetchall()
            
            today = date.today()
            today_events = []
            
            for event in all_events:
                start_at_str = event['start_at']
                
                try:
                    # Пробуем разные форматы даты
                    if 'T' in start_at_str:
                        # ISO формат с временем
                        if start_at_str.endswith('Z'):
                            event_date = datetime.fromisoformat(start_at_str[:-1]).date()
                        else:
                            event_date = datetime.fromisoformat(start_at_str).date()
                    else:
                        # Только дата
                        event_date = datetime.strptime(start_at_str, '%Y-%m-%d').date()
                    
                    if event_date == today:
                        today_events.append(event)
                        
                except (ValueError, TypeError) as e:
                    print(f"Ошибка парсинга даты события {start_at_str}: {e}")
                    continue
                    
            return today_events

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
                           t.completed, t.created_at, t.completed_at, t.project_id, p.name AS project_name, p.color AS project_color
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
                           t.completed, t.created_at, t.completed_at, t.project_id, p.name AS project_name, p.color AS project_color
                    FROM tasks t
                    LEFT JOIN projects p ON t.project_id = p.id
                    WHERE t.user_id = %s OR t.project_id IN (
                        SELECT p2.id FROM projects p2 
                        WHERE p2.owner_id = %s OR p2.id IN (
                            SELECT pm.project_id FROM project_members pm WHERE pm.user_id = %s
                        )
                    )
                    ORDER BY
                        t.completed ASC,
                        t.due_date IS NULL, t.due_date ASC,
                        CASE WHEN t.priority = 'важная' THEN 0 ELSE 1 END
                """, (user_id, user_id, user_id))
            return cur.fetchall()

def get_today_tasks(user_id: int):
    """Получить задачи на сегодня и просроченные"""
    from datetime import datetime, date
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Получаем все незавершенные задачи пользователя
            cur.execute("""
                SELECT tasks.id, tasks.title, tasks.description, tasks.due_date, tasks.priority,
                       tasks.completed, tasks.created_at, tasks.project_id,
                       projects.name AS project_name, projects.color AS project_color
                FROM tasks
                LEFT JOIN projects ON tasks.project_id = projects.id
                WHERE tasks.completed = FALSE
                  AND tasks.due_date IS NOT NULL
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
            all_tasks = cur.fetchall()
            
            today = date.today()
            overdue = []
            today_tasks = []
            
            for task in all_tasks:
                due_date_str = task['due_date']
                
                try:
                    # Пробуем разные форматы даты
                    if 'T' in due_date_str:
                        # ISO формат с временем
                        if due_date_str.endswith('Z'):
                            task_date = datetime.fromisoformat(due_date_str[:-1]).date()
                        else:
                            task_date = datetime.fromisoformat(due_date_str).date()
                    else:
                        # Только дата
                        task_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
                    
                    if task_date < today:
                        overdue.append(task)
                    elif task_date == today:
                        today_tasks.append(task)
                        
                except (ValueError, TypeError) as e:
                    print(f"Ошибка парсинга даты {due_date_str}: {e}")
                    continue

            return {"overdue": overdue, "today": today_tasks}

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
                WHERE p.owner_id = %s OR p.id IN (
                    SELECT pm.project_id FROM project_members pm WHERE pm.user_id = %s
                )
                ORDER BY p.created_at DESC
            """, (user_id, user_id))
            return cur.fetchall()

# --- Получить мероприятия пользователя (личные и проектные) ---
def get_user_events(user_id: int, filter: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            now = datetime.utcnow().isoformat()

            if filter == "Все":
                cur.execute("""
                    SELECT e.id, e.title, e.location, e.start_at, e.end_at, e.active,
                           e.description, e.type, e.participants, 
                           p.name as project_name, p.color as project_color
                    FROM events e
                    LEFT JOIN projects p ON e.project_id = p.id
                    WHERE e.active = TRUE
                      AND (
                          e.user_id = %s OR e.project_id IN (
                              SELECT p2.id FROM projects p2 
                              WHERE p2.owner_id = %s OR p2.id IN (
                                  SELECT pm.project_id FROM project_members pm WHERE pm.user_id = %s
                              )
                          )
                      )
                    ORDER BY e.start_at ASC
                """, (user_id, user_id, user_id))
            elif filter == "Прошедшие":
                cur.execute("""
                    SELECT e.id, e.title, e.location, e.start_at, e.end_at, e.active,
                           e.description, e.type, e.participants,
                           p.name as project_name, p.color as project_color
                    FROM events e
                    LEFT JOIN projects p ON e.project_id = p.id
                    WHERE e.active = TRUE AND e.end_at < %s
                      AND (
                          e.user_id = %s OR e.project_id IN (
                              SELECT p2.id FROM projects p2 
                              WHERE p2.owner_id = %s OR p2.id IN (
                                  SELECT pm.project_id FROM project_members pm WHERE pm.user_id = %s
                              )
                          )
                      )
                    ORDER BY e.start_at ASC
                """, (now, user_id, user_id, user_id))
            else:  # Предстоящие
                cur.execute("""
                    SELECT e.id, e.title, e.location, e.start_at, e.end_at, e.active,
                           e.description, e.type, e.participants,
                           p.name as project_name, p.color as project_color
                    FROM events e
                    LEFT JOIN projects p ON e.project_id = p.id
                    WHERE e.active = TRUE AND e.end_at >= %s
                      AND (
                          e.user_id = %s OR e.project_id IN (
                              SELECT p2.id FROM projects p2 
                              WHERE p2.owner_id = %s OR p2.id IN (
                                  SELECT pm.project_id FROM project_members pm WHERE pm.user_id = %s
                              )
                          )
                      )
                    ORDER BY e.start_at ASC
                """, (now, user_id, user_id, user_id))

            rows = cur.fetchall()
            print("EVENTS:", rows)
            return rows

# === Новые функции для Dashboard ===

def get_shopping_items(user_id: int):
    """Получить все покупки пользователя"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, quantity, price, category, completed, created_at
                FROM purchases 
                WHERE user_id = %s 
                ORDER BY completed ASC, created_at DESC
            """, (user_id,))
            return cur.fetchall()

def add_shopping_item(user_id: int, name: str, quantity: int = 1, price: float = None, category: str = 'other'):
    """Добавить новую покупку"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO purchases (user_id, name, quantity, price, category, completed, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (user_id, name, quantity, price, category, False, datetime.utcnow().isoformat()))
            result = cur.fetchone()
            conn.commit()
            return result['id'] if result else None

def toggle_shopping_item(item_id: int, user_id: int):
    """Переключить статус покупки"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE purchases 
                SET completed = NOT completed 
                WHERE id = %s AND user_id = %s
                RETURNING completed
            """, (item_id, user_id))
            result = cur.fetchone()
            conn.commit()
            return result['completed'] if result else None

def update_shopping_item(item_id: int, user_id: int, name: str, quantity: int = 1, price: float = None, category: str = 'other'):
    """Обновить покупку"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE purchases 
                SET name = %s, quantity = %s, price = %s, category = %s
                WHERE id = %s AND user_id = %s
                RETURNING id
            """, (name, quantity, price, category, item_id, user_id))
            result = cur.fetchone()
            conn.commit()
            return result is not None

def delete_shopping_item(item_id: int):
    """Удалить покупку"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM purchases WHERE id = %s", (item_id,))
            conn.commit()
            return cur.rowcount > 0

def get_user_stats(user_id: int):
    """Получить статистику пользователя для dashboard"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            stats = {}
            
            # Статистика задач
            cur.execute("SELECT COUNT(*) as total FROM tasks WHERE user_id = %s", (user_id,))
            stats['tasks_total'] = cur.fetchone()['total']
            
            cur.execute("SELECT COUNT(*) as completed FROM tasks WHERE user_id = %s AND completed = true", (user_id,))
            stats['tasks_completed'] = cur.fetchone()['completed']
            
            # Статистика событий
            cur.execute("SELECT COUNT(*) as total FROM events WHERE user_id = %s", (user_id,))
            stats['events_total'] = cur.fetchone()['total']
            
            # Статистика покупок
            cur.execute("SELECT COUNT(*) as total FROM purchases WHERE user_id = %s", (user_id,))
            stats['shopping_total'] = cur.fetchone()['total']
            
            return stats

def get_dashboard_counters(user_id: int):
    """Получить счетчики для навигации dashboard"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            counters = {}
            
            # Активные задачи
            cur.execute("SELECT COUNT(*) as count FROM tasks WHERE user_id = %s AND completed = false", (user_id,))
            counters['tasks'] = cur.fetchone()['count']
            
            # Предстоящие события (сегодня и в будущем)
            cur.execute("""
                SELECT COUNT(*) as count FROM events 
                WHERE user_id = %s AND start_at >= CURRENT_DATE::text AND active = true
            """, (user_id,))
            counters['events'] = cur.fetchone()['count']
            
            # Активные покупки
            cur.execute("SELECT COUNT(*) as count FROM purchases WHERE user_id = %s AND completed = false", (user_id,))
            counters['shopping'] = cur.fetchone()['count']
            
            return counters

def toggle_task_status(task_id: int, user_id: int):
    """Переключить статус задачи"""
    from datetime import datetime
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Сначала получаем текущий статус
            cur.execute("SELECT completed FROM tasks WHERE id = %s AND user_id = %s", (task_id, user_id))
            current_task = cur.fetchone()
            
            if not current_task:
                return None
                
            new_completed = not current_task['completed']
            current_time = datetime.utcnow().isoformat()
            
            if new_completed:
                # Задача завершается - устанавливаем completed_at
                cur.execute("""
                    UPDATE tasks 
                    SET completed = TRUE, completed_at = %s
                    WHERE id = %s AND user_id = %s
                    RETURNING completed
                """, (current_time, task_id, user_id))
            else:
                # Задача возвращается в работу - очищаем completed_at
                cur.execute("""
                    UPDATE tasks 
                    SET completed = FALSE, completed_at = NULL
                    WHERE id = %s AND user_id = %s
                    RETURNING completed
                """, (task_id, user_id))
            
            result = cur.fetchone()
            conn.commit()
            return result['completed'] if result else None

def delete_event_by_id(event_id: int):
    """Удалить событие по ID"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM events WHERE id = %s", (event_id,))
            conn.commit()
            return cur.rowcount > 0

def clear_user_data(user_id: int):
    """Очистить все данные пользователя"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Удаляем все данные пользователя
            cur.execute("DELETE FROM tasks WHERE user_id = %s", (user_id,))
            cur.execute("DELETE FROM events WHERE user_id = %s", (user_id,))
            cur.execute("DELETE FROM purchases WHERE user_id = %s", (user_id,))
            cur.execute("DELETE FROM projects WHERE user_id = %s", (user_id,))
            cur.execute("DELETE FROM notes WHERE user_id = %s", (user_id,))
            
            conn.commit()
            return True

# === Notes Functions ===

def add_note(user_id: int, title: str, content: str):
    """Добавить новую заметку"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO notes (user_id, title, content, created_at, updated_at)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                RETURNING id
            """, (user_id, title, content))
            
            note_id = cur.fetchone()['id']
            conn.commit()
            return note_id

def get_user_notes(user_id: int):
    """Получить все заметки пользователя"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, content, created_at, updated_at
                FROM notes
                WHERE user_id = %s
                ORDER BY created_at DESC
            """, (user_id,))
            
            return [dict(row) for row in cur.fetchall()]

def get_note_by_id(note_id: int, user_id: int):
    """Получить заметку по ID"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, content, created_at, updated_at
                FROM notes
                WHERE id = %s AND user_id = %s
            """, (note_id, user_id))
            
            row = cur.fetchone()
            return dict(row) if row else None

def update_note(note_id: int, user_id: int, title: str, content: str):
    """Обновить заметку"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE notes
                SET title = %s, content = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s AND user_id = %s
            """, (title, content, note_id, user_id))
            
            conn.commit()
            return cur.rowcount > 0

def delete_note(note_id: int, user_id: int):
    """Удалить заметку"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM notes
                WHERE id = %s AND user_id = %s
            """, (note_id, user_id))
            
            conn.commit()
            return cur.rowcount > 0

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
    # Новые функции для Dashboard
    "get_shopping_items",
    "add_shopping_item",
    "toggle_shopping_item",
    "delete_shopping_item",
    "get_user_stats",
    "get_dashboard_counters",
    "toggle_task_status",
    "delete_event_by_id",
    "clear_user_data",
    # Notes functions
    "add_note",
    "get_user_notes",
    "get_note_by_id",
    "update_note",
    "delete_note",
]