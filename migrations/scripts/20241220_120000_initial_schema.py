"""
Начальная миграция - создание базовой схемы БД
"""

def up(cursor):
    """Применить миграцию"""
    
    # Пользователи
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            first_name TEXT,
            username TEXT,
            registered_at TEXT
        );
    """)

    # Проекты
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            owner_id BIGINT NOT NULL REFERENCES users(user_id),
            color TEXT,
            created_at TEXT
        );
    """)

    # Покупки
    cursor.execute("""
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
    cursor.execute("""
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

    # Логи
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            type TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT
        );
    """)

    # Логи отправленных напоминаний
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminder_logs (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            event_id INTEGER NOT NULL,
            sent_at TEXT
        );
    """)

    # Задачи
    cursor.execute("""
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_members (
            id SERIAL PRIMARY KEY,
            project_id INTEGER REFERENCES projects(id),
            user_id BIGINT NOT NULL,
            joined_at TEXT,
            UNIQUE (project_id, user_id)
        );
    """)

    # Настройки пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id BIGINT NOT NULL,
            key TEXT NOT NULL,
            value TEXT,
            PRIMARY KEY (user_id, key)
        );
    """)

    print("✅ Базовая схема создана")


def down(cursor):
    """Откатить миграцию"""
    
    tables = [
        'user_settings',
        'project_members', 
        'tasks',
        'reminder_logs',
        'logs',
        'events',
        'shopping',
        'projects',
        'users'
    ]
    
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
    
    print("✅ Базовая схема удалена")