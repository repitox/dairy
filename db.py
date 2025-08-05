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

# Устанавливаем DATABASE_URL для продакшена NetAngels если не задан
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Для NetAngels dialist.ru
    DATABASE_URL = "postgresql://c107597_dialist_ru:ZoXboBiphobem19@postgres.c107597.h2:5432/c107597_dialist_ru"
    os.environ["DATABASE_URL"] = DATABASE_URL
    print(f"🔧 Установлен DATABASE_URL для NetAngels: {DATABASE_URL[:50]}...")

def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

# Создание всех таблиц
def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Пользователи (новая структура после миграции)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    telegram_id BIGINT UNIQUE NOT NULL,
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
                    owner_id INTEGER NOT NULL REFERENCES users(id),
                    color TEXT,
                    created_at TEXT,
                    active BOOLEAN DEFAULT TRUE
                );
            """)

            # Покупки
            cur.execute("""
                CREATE TABLE IF NOT EXISTS shopping (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER,
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
                    user_id INTEGER,
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
                    user_id INTEGER NOT NULL,
                    event_id INTEGER NOT NULL,
                    sent_at TEXT
                );
            """)

            # Задачи
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
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
                    user_id INTEGER NOT NULL,
                    joined_at TEXT,
                    UNIQUE (project_id, user_id)
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id INTEGER NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT,
                    PRIMARY KEY (user_id, key)
                );
            """)

            # Заметки
            cur.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    title TEXT NOT NULL,
                    content TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Покупки (новая таблица)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS purchases (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    project_id INTEGER REFERENCES projects(id),
                    name TEXT NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 1,
                    price DECIMAL(10,2),
                    category TEXT DEFAULT 'other',
                    completed BOOLEAN DEFAULT FALSE,
                    created_at TEXT,
                    shopping_list_id INTEGER,
                    url TEXT,
                    comment TEXT
                );
            """)

            # Списки покупок
            cur.execute("""
                CREATE TABLE IF NOT EXISTS shopping_lists (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    project_id INTEGER NOT NULL REFERENCES projects(id),
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    created_at TEXT,
                    active BOOLEAN DEFAULT TRUE
                );
            """)

            # Участники проектов
            cur.execute("""
                CREATE TABLE IF NOT EXISTS project_members (
                    project_id INTEGER NOT NULL REFERENCES projects(id),
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    joined_at TEXT,
                    PRIMARY KEY (project_id, user_id)
                );
            """)

            # Индексы для производительности
            cur.execute("CREATE INDEX IF NOT EXISTS idx_purchases_user_id ON purchases(user_id);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_purchases_completed ON purchases(completed);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_purchases_shopping_list_id ON purchases(shopping_list_id);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_shopping_lists_user_id ON shopping_lists(user_id);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_project_members_project_id ON project_members(project_id);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_project_members_user_id ON project_members(user_id);")

            conn.commit()

# ✅ Пользователи
def add_user(user_id: int, first_name: str, username: str):
    """
    Добавляет пользователя в БД с новой структурой после миграции.
    user_id - это telegram_id пользователя
    """
    print(f"🗄 Добавляем пользователя: {user_id}, {first_name}, {username}")
    with get_conn() as conn:
        with conn.cursor() as cur:
            try:
                # Вставляем пользователя с новой структурой
                cur.execute("""
                    INSERT INTO users (telegram_id, first_name, username, registered_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (telegram_id) DO NOTHING
                    RETURNING id;
                """, (user_id, first_name, username, datetime.utcnow().isoformat()))
                
                # Получаем ID пользователя (новый автоинкрементный или существующий)
                result = cur.fetchone()
                if result:
                    internal_user_id = result['id']
                    print(f"✅ Создан новый пользователь с id={internal_user_id}")
                else:
                    # Пользователь уже существует, получаем его ID
                    cur.execute("SELECT id FROM users WHERE telegram_id = %s", (user_id,))
                    internal_user_id = cur.fetchone()['id']
                    print(f"✅ Пользователь уже существует с id={internal_user_id}")
                
                # Создаем личный проект для пользователя, используя внутренний ID
                # Сначала проверяем, существует ли проект
                cur.execute("SELECT id FROM projects WHERE owner_id = %s AND name = 'Личное'", (internal_user_id,))
                existing_project = cur.fetchone()
                
                if existing_project:
                    personal_project_id = existing_project['id']
                    print(f"✅ Личный проект уже существует с ID {personal_project_id}")
                else:
                    # Создаем новый проект
                    cur.execute("""
                        INSERT INTO projects (name, owner_id, color, created_at, active)
                        VALUES ('Личное', %s, '#6366f1', %s, TRUE)
                        RETURNING id;
                    """, (internal_user_id, datetime.utcnow().isoformat()))
                    
                    project_result = cur.fetchone()
                    personal_project_id = project_result['id']
                    print(f"✅ Создан новый личный проект с ID {personal_project_id}")
                
                # Добавляем пользователя как участника своего личного проекта
                cur.execute("""
                    INSERT INTO project_members (project_id, user_id, joined_at)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (project_id, user_id) DO NOTHING;
                """, (personal_project_id, internal_user_id, datetime.utcnow().isoformat()))
                
                conn.commit()
                print("✅ Пользователь добавлен (или уже существует)")
                return internal_user_id
            except Exception as e:
                print("❌ Ошибка при добавлении пользователя:", e)
                return None

def get_user_personal_project_id(internal_user_id: int) -> int:
    """
    Получить ID личного проекта пользователя по внутреннему ID пользователя
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Ищем проект по внутреннему ID пользователя (projects.owner_id = users.id)
            cur.execute("""
                SELECT id FROM projects 
                WHERE owner_id = %s AND name = 'Личное' AND active = TRUE
                LIMIT 1
            """, (internal_user_id,))
            result = cur.fetchone()
            if result:
                return result['id']
            else:
                return None

def get_user_db_id(telegram_id: int) -> int:
    """
    Получить ID пользователя из БД по telegram_id
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
            result = cur.fetchone()
            return result['id'] if result else None

def resolve_user_id(user_id: int) -> int:
    """
    Умная функция для получения внутреннего ID пользователя.
    Сначала проверяет, является ли user_id уже внутренним ID (малое число),
    если нет - ищет по telegram_id (большое число).
    """
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Если user_id маленький (< 1000000), возможно это уже ID из БД
            if user_id < 1000000:
                # Проверяем, существует ли пользователь с таким ID
                cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
                result = cur.fetchone()
                if result:
                    return result['id']
            
            # Если не найден как ID из БД или user_id большой, ищем по telegram_id
            cur.execute("SELECT id FROM users WHERE telegram_id = %s", (user_id,))
            result = cur.fetchone()
            return result['id'] if result else None

def get_personal_project_id(user_id: int) -> int:
    """
    УСТАРЕВШАЯ ФУНКЦИЯ - используйте get_user_personal_project_id()
    Получить ID личного проекта пользователя
    """
    return get_user_personal_project_id(user_id)

# Универсальная функция для обновления любой настройки пользователя
def update_user_setting(user_id: int, key: str, value: str):
    """
    Обновляет настройку пользователя. user_id может быть telegram_id или ID из БД.
    """
    db_user_id = resolve_user_id(user_id)
    if not db_user_id:
        print(f"❌ Пользователь с ID {user_id} не найден")
        return
        
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO user_settings (user_id, key, value)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, key) DO UPDATE SET value = EXCLUDED.value
            """, (db_user_id, key, value))
            conn.commit()

# Универсальная функция для получения всех настроек пользователя
def get_user_settings(user_id: int) -> dict:
    """
    Получает все настройки пользователя. user_id может быть telegram_id или ID из БД.
    """
    db_user_id = resolve_user_id(user_id)
    if not db_user_id:
        return {}
        
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT key, value FROM user_settings WHERE user_id = %s
            """, (db_user_id,))
            rows = cur.fetchall()
            return {row["key"]: row["value"] for row in rows}

# Получить конкретную настройку пользователя по ключу
def get_user_setting(user_id: int, key: str) -> str:
    """
    Получает конкретную настройку пользователя. user_id может быть telegram_id или ID из БД.
    """
    db_user_id = resolve_user_id(user_id)
    if not db_user_id:
        return None
        
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT value FROM user_settings
                WHERE user_id = %s AND key = %s
            """, (db_user_id, key))
            row = cur.fetchone()
            return row["value"] if row else None

# ✅ Покупки
def add_purchase(user_id: int, project_id: int, item: str, quantity: int):
    """
    Создает новую покупку. user_id может быть telegram_id или ID из БД.
    """
    db_user_id = resolve_user_id(user_id)
    if not db_user_id:
        print(f"❌ Пользователь с ID {user_id} не найден")
        return None
        
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO shopping (user_id, project_id, item, quantity, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (db_user_id, project_id, item, quantity, 'Нужно купить', datetime.utcnow().isoformat()))
            purchase_id = cur.fetchone()['id']
            conn.commit()
            print(f"✅ Покупка создана с ID {purchase_id} для пользователя {db_user_id}")
            return purchase_id

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
    """
    Получает последние покупки пользователя. user_id может быть telegram_id или ID из БД.
    """
    db_user_id = resolve_user_id(user_id)
    if not db_user_id:
        print(f"❌ Пользователь с ID {user_id} не найден")
        return []
        
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    p.id, 
                    p.name as item, 
                    p.name as title,
                    p.quantity, 
                  CASE WHEN p.completed THEN 'Куплено' ELSE 'Нужно купить' END as status,
                    p.completed as is_done,
                    p.created_at,
                    p.price,
                      p.category
                FROM purchases p
                WHERE p.completed = FALSE
                  AND p.user_id = %s
                ORDER BY p.created_at DESC
                LIMIT %s
            """, (db_user_id, limit))
            return cur.fetchall()


def update_purchase_status(purchase_id: int, new_status: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE shopping SET status = %s WHERE id = %s
            """, (new_status, purchase_id))
            conn.commit()

# ✅ Мероприятия
def add_event(user_id: int, project_id: int, title: str, location: str, start_at: str = None, end_at: str = None, description: str = None):
    """
    Создает новое событие. user_id может быть telegram_id или ID из БД.
    """
    db_user_id = resolve_user_id(user_id)
    if not db_user_id:
        print(f"❌ Пользователь с ID {user_id} не найден")
        return None
        
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO events (user_id, project_id, title, location, start_at, end_at, created_at, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (db_user_id, project_id, title, location, start_at, end_at, datetime.utcnow().isoformat(), description))
            event_id = cur.fetchone()['id']
            conn.commit()
            print(f"✅ Событие создано с ID {event_id} для пользователя {db_user_id}")
            return event_id

def update_event(event_id: int, user_id: int, title: str, location: str, start_at: str, end_at: str):
    """
    Обновляет событие. user_id может быть telegram_id или ID из БД.
    """
    db_user_id = resolve_user_id(user_id)
    if not db_user_id:
        print(f"❌ Пользователь с ID {user_id} не найден")
        return False
        
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
            """, (db_user_id, title, location, start_at, end_at, event_id))
            conn.commit()
            print(f"✅ Событие {event_id} обновлено для пользователя {db_user_id}")
            return True

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
    """
    Получает события по фильтру. user_id может быть telegram_id или ID из БД.
    """
    db_user_id = resolve_user_id(user_id)
    if not db_user_id:
        print(f"❌ Пользователь с ID {user_id} не найден")
        return []
        
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
                """, (db_user_id, db_user_id))
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
                """, (now, db_user_id, db_user_id))
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
                """, (now, db_user_id, db_user_id))

            return cur.fetchall()

def get_today_events(user_id: int):
    """
    Получить события на сегодня. user_id может быть telegram_id или ID из БД.
    """
    from datetime import datetime, date
    
    db_user_id = resolve_user_id(user_id)
    if not db_user_id:
        print(f"❌ Пользователь с ID {user_id} не найден")
        return []
    
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
            """, (db_user_id, db_user_id))
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
    """
    Проверяет, было ли отправлено напоминание. user_id может быть telegram_id или ID из БД.
    """
    db_user_id = resolve_user_id(user_id)
    if not db_user_id:
        print(f"❌ Пользователь с ID {user_id} не найден")
        return False
        
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 1 FROM reminder_logs
                WHERE user_id = %s AND event_id = %s
                LIMIT 1;
            """, (db_user_id, event_id))
            return cur.fetchone() is not None

def record_reminder_sent(user_id: int, event_id: int):
    """
    Записывает отправку напоминания. user_id может быть telegram_id или ID из БД.
    """
    db_user_id = resolve_user_id(user_id)
    if not db_user_id:
        print(f"❌ Пользователь с ID {user_id} не найден")
        return False
        
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO reminder_logs (user_id, event_id, sent_at)
                VALUES (%s, %s, %s)
            """, (db_user_id, event_id, datetime.utcnow().isoformat()))
            conn.commit()
            print(f"✅ Напоминание записано для пользователя {db_user_id}, событие {event_id}")
            return True

# --- Задачи ---
def add_task(user_id: int, project_id: int, title: str, due_date: str, priority: str, description: str = ""):
    """
    Создает новую задачу. user_id может быть telegram_id или ID из БД.
    """
    db_user_id = resolve_user_id(user_id)
    if not db_user_id:
        print(f"❌ Пользователь с ID {user_id} не найден")
        return None
        
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tasks (user_id, project_id, title, description, due_date, priority, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (db_user_id, project_id, title, description, due_date, priority, datetime.utcnow().isoformat()))
            task_id = cur.fetchone()['id']
            conn.commit()
            print(f"✅ Задача создана с ID {task_id} для пользователя {db_user_id}")
            return task_id

from typing import Optional

def get_tasks(user_id: int, project_id: Optional[int] = None):
    """
    Получает задачи пользователя. user_id может быть telegram_id или ID из БД.
    """
    db_user_id = resolve_user_id(user_id)
    if not db_user_id:
        print(f"❌ Пользователь с ID {user_id} не найден")
        return []
        
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
                """, (db_user_id, db_user_id, db_user_id))
            return cur.fetchall()

def get_today_tasks(user_id: int):
    """
    Получить задачи на сегодня и просроченные. user_id может быть telegram_id или ID из БД.
    """
    from datetime import datetime, date
    
    db_user_id = resolve_user_id(user_id)
    if not db_user_id:
        print(f"❌ Пользователь с ID {user_id} не найден")
        return {"overdue": [], "today": []}
    
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
            """, (db_user_id, db_user_id))
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
            
            # Добавляем владельца как участника проекта
            with conn.cursor() as cur2:
                cur2.execute("""
                    INSERT INTO project_members (project_id, user_id, joined_at)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (project_id, user_id) DO NOTHING
                """, (project_id, owner_id, datetime.utcnow().isoformat()))
                conn.commit()
            
            return project_id

def update_project(project_id: int, name: str, color: str, owner_id: int):
    """Обновить проект (только владелец может обновлять)"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE projects 
                SET name = %s, color = %s
                WHERE id = %s AND owner_id = %s
                RETURNING id;
            """, (name, color, project_id, owner_id))
            result = cur.fetchone()
            conn.commit()
            return result is not None

def delete_project(project_id: int, user_id: int):
    """
    Удалить проект (только владелец может удалять). user_id может быть telegram_id или ID из БД.
    """
    db_user_id = resolve_user_id(user_id)
    if not db_user_id:
        print(f"❌ Пользователь с ID {user_id} не найден")
        return False
        
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Сначала проверим, что пользователь является владельцем
            cur.execute("""
                SELECT id FROM projects 
                WHERE id = %s AND owner_id = %s
            """, (project_id, db_user_id))
            
            if not cur.fetchone():
                print(f"❌ Пользователь {db_user_id} не является владельцем проекта {project_id}")
                return False
            
            # Удаляем связанные данные в правильном порядке
            # 1. Удаляем участников проекта
            cur.execute("DELETE FROM project_members WHERE project_id = %s", (project_id,))
            
            # 2. Удаляем задачи проекта
            cur.execute("DELETE FROM tasks WHERE project_id = %s", (project_id,))
            
            # 3. Удаляем события проекта
            cur.execute("DELETE FROM events WHERE project_id = %s", (project_id,))
            
            # 4. Удаляем покупки проекта
            cur.execute("DELETE FROM purchases WHERE project_id = %s", (project_id,))
            
            # 5. Удаляем списки покупок проекта
            cur.execute("DELETE FROM shopping_lists WHERE project_id = %s", (project_id,))
            
            # 6. Наконец, удаляем сам проект
            cur.execute("DELETE FROM projects WHERE id = %s", (project_id,))
            
            conn.commit()
            print(f"✅ Проект {project_id} успешно удален пользователем {db_user_id}")
            return True

# --- Участники проекта ---
# Старая функция удалена, используется новая версия ниже

def get_project(project_id: int, user_id: int = None):
    """
    Получает проект по ID. user_id может быть telegram_id или ID из БД.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            if user_id:
                db_user_id = resolve_user_id(user_id)
                if not db_user_id:
                    print(f"❌ Пользователь с ID {user_id} не найден")
                    return None
                    
                # Проверяем доступ пользователя к проекту
                cur.execute("""
                    SELECT p.id, p.name, p.color, p.owner_id, p.created_at
                    FROM projects p
                    WHERE p.id = %s AND p.active = TRUE
                    AND (p.owner_id = %s OR p.id IN (
                        SELECT pm.project_id FROM project_members pm WHERE pm.user_id = %s
                    ))
                """, (project_id, db_user_id, db_user_id))
            else:
                cur.execute("""
                    SELECT p.id, p.name, p.color, p.owner_id, p.created_at
                    FROM projects p
                    WHERE p.id = %s AND p.active = TRUE
                """, (project_id,))
            return cur.fetchone()

# --- Получить проекты пользователя ---
def get_user_projects(user_id: int):
    """
    Получает проекты пользователя. user_id может быть telegram_id или ID из БД.
    """
    db_user_id = resolve_user_id(user_id)
    if not db_user_id:
        print(f"❌ Пользователь с ID {user_id} не найден")
        return []
        
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.id, p.name, p.color, p.created_at
                FROM projects p
                WHERE (p.owner_id = %s OR p.id IN (
                    SELECT pm.project_id FROM project_members pm WHERE pm.user_id = %s
                )) AND p.active = TRUE
                ORDER BY p.created_at DESC
            """, (db_user_id, db_user_id))
            return cur.fetchall()

def deactivate_project(project_id: int, user_id: int):
    """Деактивировать проект (только владелец может деактивировать)"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Проверяем, что пользователь является владельцем проекта
            cur.execute("""
                UPDATE projects 
                SET active = FALSE 
                WHERE id = %s AND owner_id = %s AND active = TRUE
                RETURNING id
            """, (project_id, user_id))
            result = cur.fetchone()
            conn.commit()
            return result is not None

def get_project_members(project_id: int, user_id: int):
    """Получить участников проекта"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Сначала проверяем доступ пользователя к проекту
            cur.execute("""
                SELECT 1 FROM projects p
                WHERE p.id = %s AND p.active = TRUE
                AND (p.owner_id = %s OR p.id IN (
                    SELECT pm.project_id FROM project_members pm WHERE pm.user_id = %s
                ))
            """, (project_id, user_id, user_id))
            
            if not cur.fetchone():
                return []
            
            # Получаем участников проекта
            cur.execute("""
                SELECT 
                    pm.user_id,
                    u.first_name,
                    u.username,
                    CASE 
                        WHEN p.owner_id = pm.user_id THEN 'owner'
                        ELSE 'member'
                    END as role,
                    pm.joined_at
                FROM project_members pm
                JOIN users u ON u.id = pm.user_id
                JOIN projects p ON p.id = pm.project_id
                WHERE pm.project_id = %s
                ORDER BY 
                    CASE WHEN p.owner_id = pm.user_id THEN 0 ELSE 1 END,
                    pm.joined_at
            """, (project_id,))
            return cur.fetchall()

def add_project_member(project_id: int, user_id: int, member_user_id: int):
    """
    Добавить участника в проект. 
    user_id - владелец проекта (может быть telegram_id или db_user_id)
    member_user_id - добавляемый пользователь (может быть telegram_id или db_user_id)
    """
    # Определяем ID из БД для владельца проекта
    owner_db_user_id = resolve_user_id(user_id)
    if not owner_db_user_id:
        print(f"❌ Владелец проекта с ID {user_id} не найден")
        return False
    
    # Определяем ID из БД для добавляемого участника
    member_db_user_id = resolve_user_id(member_user_id)
    if not member_db_user_id:
        print(f"❌ Пользователь для добавления с ID {member_user_id} не найден")
        return False
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Проверяем, что пользователь является владельцем проекта
            cur.execute("""
                SELECT 1 FROM projects 
                WHERE id = %s AND owner_id = %s AND active = TRUE
            """, (project_id, owner_db_user_id))
            
            if not cur.fetchone():
                print(f"❌ Пользователь {owner_db_user_id} не является владельцем проекта {project_id}")
                return False
            
            # Добавляем участника
            try:
                cur.execute("""
                    INSERT INTO project_members (project_id, user_id, joined_at)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (project_id, user_id) DO NOTHING
                """, (project_id, member_db_user_id, datetime.utcnow().isoformat()))
                conn.commit()
                print(f"✅ Пользователь {member_db_user_id} добавлен в проект {project_id}")
                return True
            except Exception as e:
                print(f"❌ Ошибка добавления участника: {e}")
                return False

def remove_project_member(project_id: int, user_id: int, member_user_id: int):
    """Удалить участника из проекта"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Проверяем, что пользователь является владельцем проекта
            cur.execute("""
                SELECT owner_id FROM projects 
                WHERE id = %s AND owner_id = %s AND active = TRUE
            """, (project_id, user_id))
            
            if not cur.fetchone():
                return False
            
            # Не позволяем удалить владельца
            cur.execute("""
                SELECT 1 FROM projects 
                WHERE id = %s AND owner_id = %s
            """, (project_id, member_user_id))
            
            if cur.fetchone():
                return False  # Нельзя удалить владельца
            
            # Удаляем участника
            cur.execute("""
                DELETE FROM project_members 
                WHERE project_id = %s AND user_id = %s
            """, (project_id, member_user_id))
            conn.commit()
            return True

# --- Получить мероприятия пользователя (личные и проектные) ---
def get_user_events(user_id: int, filter: str):
    # Преобразуем telegram_id в ID из БД если нужно
    db_user_id = resolve_user_id(user_id)
    if not db_user_id:
        print(f"❌ Пользователь с ID {user_id} не найден")
        return []
        
    with get_conn() as conn:
        with conn.cursor() as cur:
            now = datetime.utcnow().isoformat()

            if filter == "Все":
                cur.execute("""
                    SELECT e.id, e.title, e.location, e.start_at, e.end_at, e.active,
                           e.description, e.created_at,
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
                """, (db_user_id, db_user_id, db_user_id))
            elif filter == "Прошедшие":
                cur.execute("""
                    SELECT e.id, e.title, e.location, e.start_at, e.end_at, e.active,
                           e.description, e.created_at,
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
                """, (now, db_user_id, db_user_id, db_user_id))
            else:  # Предстоящие
                cur.execute("""
                    SELECT e.id, e.title, e.location, e.start_at, e.end_at, e.active,
                           e.description, e.created_at,
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
                """, (now, db_user_id, db_user_id, db_user_id))

            rows = cur.fetchall()
            print("EVENTS:", rows)
            return rows

# === Новые функции для Dashboard ===

def get_shopping_items(user_id: int):
    """
    Получить все покупки пользователя. user_id может быть telegram_id или ID из БД.
    """
    db_user_id = resolve_user_id(user_id)
    if not db_user_id:
        print(f"❌ Пользователь с ID {user_id} не найден")
        return []
        
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, quantity, price, category, completed, created_at, 
                       shopping_list_id, url, comment
                FROM purchases 
                WHERE user_id = %s 
                ORDER BY completed ASC, created_at DESC
            """, (db_user_id,))
            return cur.fetchall()

def add_shopping_item(user_id: int, name: str, quantity: int = 1, price: float = None, category: str = 'other', shopping_list_id: int = None, url: str = None, comment: str = None):
    """
    Добавить новую покупку. user_id может быть telegram_id или ID из БД.
    """
    db_user_id = resolve_user_id(user_id)
    if not db_user_id:
        print(f"❌ Пользователь с ID {user_id} не найден")
        return None
        
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO purchases (user_id, name, quantity, price, category, completed, created_at, shopping_list_id, url, comment)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (db_user_id, name, quantity, price, category, False, datetime.utcnow().isoformat(), shopping_list_id, url, comment))
            result = cur.fetchone()
            conn.commit()
            print(f"✅ Товар добавлен с ID {result['id']} для пользователя {db_user_id}")
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

def update_shopping_item(item_id: int, user_id: int, name: str, quantity: int = 1, price: float = None, category: str = 'other', shopping_list_id: int = None, url: str = None, comment: str = None):
    """Обновить покупку"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE purchases 
                SET name = %s, quantity = %s, price = %s, category = %s, shopping_list_id = %s, url = %s, comment = %s
                WHERE id = %s AND user_id = %s
                RETURNING id
            """, (name, quantity, price, category, shopping_list_id, url, comment, item_id, user_id))
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

# --- Функции для работы со списками покупок ---

def get_user_shopping_lists(user_id: int):
    """Получить все списки покупок пользователя"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT sl.id, sl.name, sl.project_id, p.name as project_name, p.color as project_color,
                       sl.created_at,
                       COUNT(pu.id) as total_items,
                       COUNT(CASE WHEN pu.completed = true THEN 1 END) as completed_items
                FROM shopping_lists sl
                LEFT JOIN projects p ON sl.project_id = p.id
                LEFT JOIN purchases pu ON sl.id = pu.shopping_list_id
                WHERE sl.user_id = %s
                GROUP BY sl.id, sl.name, sl.project_id, p.name, p.color, sl.created_at
                ORDER BY sl.created_at DESC
            """, (user_id,))
            return cur.fetchall()

def create_shopping_list(user_id: int, name: str, project_id: int):
    """
    Создать новый список покупок. user_id может быть telegram_id или ID из БД.
    """
    db_user_id = resolve_user_id(user_id)
    if not db_user_id:
        print(f"❌ Пользователь с ID {user_id} не найден")
        return None
        
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Проверяем, что пользователь имеет доступ к проекту
            cur.execute("""
                SELECT 1 FROM projects p
                WHERE p.id = %s AND (
                    p.owner_id = %s OR 
                    EXISTS (SELECT 1 FROM project_members pm WHERE pm.project_id = %s AND pm.user_id = %s)
                )
            """, (project_id, db_user_id, project_id, db_user_id))
            
            if not cur.fetchone():
                print(f"❌ Пользователь {db_user_id} не имеет доступа к проекту {project_id}")
                return None
            
            cur.execute("""
                INSERT INTO shopping_lists (name, project_id, user_id, created_at)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (name, project_id, db_user_id, datetime.utcnow().isoformat()))
            result = cur.fetchone()
            conn.commit()
            print(f"✅ Список покупок создан с ID {result['id']} для пользователя {db_user_id}")
            return result['id'] if result else None

def get_shopping_list(list_id: int, user_id: int):
    """Получить информацию о списке покупок"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT sl.id, sl.name, sl.project_id, p.name as project_name, p.color as project_color
                FROM shopping_lists sl
                LEFT JOIN projects p ON sl.project_id = p.id
                WHERE sl.id = %s AND sl.user_id = %s
            """, (list_id, user_id))
            return cur.fetchone()

def update_shopping_list(list_id: int, user_id: int, name: str, project_id: int):
    """Обновить список покупок"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Проверяем доступ к проекту
            cur.execute("""
                SELECT 1 FROM projects p
                WHERE p.id = %s AND (
                    p.owner_id = %s OR 
                    EXISTS (SELECT 1 FROM project_members pm WHERE pm.project_id = %s AND pm.user_id = %s)
                )
            """, (project_id, user_id, project_id, user_id))
            
            if not cur.fetchone():
                raise ValueError("У пользователя нет доступа к указанному проекту")
            
            cur.execute("""
                UPDATE shopping_lists 
                SET name = %s, project_id = %s
                WHERE id = %s AND user_id = %s
                RETURNING id
            """, (name, project_id, list_id, user_id))
            result = cur.fetchone()
            conn.commit()
            return result is not None

def delete_shopping_list(list_id: int, user_id: int):
    """Удалить список покупок"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Сначала удаляем все покупки из списка
            cur.execute("DELETE FROM purchases WHERE shopping_list_id = %s", (list_id,))
            
            # Затем удаляем сам список
            cur.execute("DELETE FROM shopping_lists WHERE id = %s AND user_id = %s", (list_id, user_id))
            conn.commit()
            return cur.rowcount > 0

def get_shopping_items_by_lists(user_id: int):
    """Получить все покупки пользователя, сгруппированные по спискам"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    sl.id as list_id, sl.name as list_name, sl.project_id,
                    p.name as project_name, p.color as project_color,
                    pu.id, pu.name, pu.quantity, pu.price, pu.category, 
                    pu.completed, pu.created_at, pu.url, pu.comment
                FROM shopping_lists sl
                LEFT JOIN projects p ON sl.project_id = p.id
                LEFT JOIN purchases pu ON sl.id = pu.shopping_list_id
                WHERE sl.user_id = %s
                ORDER BY sl.created_at DESC, pu.completed ASC, pu.created_at DESC
            """, (user_id,))
            return cur.fetchall()

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
    """
    Добавить новую заметку. user_id может быть telegram_id или ID из БД.
    """
    db_user_id = resolve_user_id(user_id)
    if not db_user_id:
        print(f"❌ Пользователь с ID {user_id} не найден")
        return None
        
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO notes (user_id, title, content, created_at, updated_at)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                RETURNING id
            """, (db_user_id, title, content))
            
            note_id = cur.fetchone()['id']
            conn.commit()
            print(f"✅ Заметка создана с ID {note_id} для пользователя {db_user_id}")
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