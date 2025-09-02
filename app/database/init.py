"""
Инициализация базы данных
"""
import os
from app.database.connection import get_db_connection
from app.core.config import settings


def initialize_database():
    """Инициализация базы данных"""
    try:
        # Устанавливаем DATABASE_URL если не установлен (для NetAngels)
        if not os.getenv("DATABASE_URL") and os.getenv("DB_CONNECTION_STRING"):
            os.environ["DATABASE_URL"] = os.getenv("DB_CONNECTION_STRING")
        
        print("🗄️ Инициализация базы данных...")
        print(f"📍 DATABASE_URL: {settings.DATABASE_URL[:50]}...")
        
        init_db()
        print("✅ База данных готова!")
        return True
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")
        # Не завершаем работу, так как таблицы могут уже существовать
        import traceback
        traceback.print_exc()
        return False


def init_db():
    """Создание всех таблиц"""
    with get_db_connection() as conn:
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

            # Покупки (старая таблица для совместимости)
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

            # Дни рождения
            cur.execute("""
                CREATE TABLE IF NOT EXISTS birthdays (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    full_name TEXT NOT NULL,
                    day INTEGER NOT NULL CHECK (day BETWEEN 1 AND 31),
                    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
                    year INTEGER,
                    description TEXT,
                    created_at TEXT
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
