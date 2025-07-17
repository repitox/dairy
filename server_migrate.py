#!/usr/bin/env python3
"""
🖥️ Скрипт для выполнения миграций на сервере NetAngels
Этот файл нужно загрузить на сервер и запустить там
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Настройки подключения к БД NetAngels
DB_CONFIG = {
    'host': 'postgres.c107597.h2',
    'database': 'c107597_rptx_na4u_ru',
    'user': 'c107597_rptx_na4u_ru',
    'password': 'ZiKceXoydixol93',
    'port': 5432
}

def get_conn():
    """Получить подключение к БД"""
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

def ensure_migrations_table():
    """Создать таблицу для отслеживания миграций"""
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        id SERIAL PRIMARY KEY,
                        version VARCHAR(255) UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        checksum TEXT
                    );
                """)
                conn.commit()
                print("✅ Таблица миграций готова")
    except Exception as e:
        print(f"❌ Ошибка создания таблицы миграций: {e}")
        raise

def get_executed_migrations():
    """Получить список выполненных миграций"""
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version FROM schema_migrations ORDER BY version")
                return [row['version'] for row in cur.fetchall()]
    except Exception as e:
        print(f"❌ Ошибка получения списка миграций: {e}")
        return []

def execute_migration(version, name, migration_func):
    """Выполнить одну миграцию"""
    print(f"🔄 Выполняем миграцию: {version} - {name}")
    
    try:
        with get_conn() as conn:
            try:
                with conn.cursor() as cur:
                    # Выполняем миграцию
                    migration_func(cur)
                    
                    # Записываем в таблицу миграций
                    cur.execute("""
                        INSERT INTO schema_migrations (version, name)
                        VALUES (%s, %s)
                    """, (version, name))
                    
                conn.commit()
                print(f"✅ Миграция {version} выполнена успешно")
                return True
                
            except Exception as e:
                conn.rollback()
                print(f"❌ Ошибка выполнения миграции {version}: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Ошибка подключения при выполнении миграции {version}: {e}")
        return False

# === МИГРАЦИИ ===

def migration_20241220_120000_initial_schema(cursor):
    """Начальная миграция - создание базовой схемы БД"""
    
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

def migration_20241220_120001_add_extended_fields(cursor):
    """Добавление расширенных полей в существующие таблицы"""
    
    # Добавляем поля в events
    cursor.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'events' AND column_name = 'type';
    """)
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE events ADD COLUMN type TEXT DEFAULT 'other';")
        print("✅ Добавлено поле type в events")
    
    cursor.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'events' AND column_name = 'participants';
    """)
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE events ADD COLUMN participants TEXT;")
        print("✅ Добавлено поле participants в events")
    
    # Добавляем поля в tasks
    cursor.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'tasks' AND column_name = 'category';
    """)
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE tasks ADD COLUMN category TEXT DEFAULT 'general';")
        print("✅ Добавлено поле category в tasks")
    
    # Создаем индексы для производительности
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_start_at ON events(start_at);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_shopping_user_id ON shopping(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_shopping_status ON shopping(status);")
    
    print("✅ Индексы созданы")

def migration_20241220_120002_create_purchases_table(cursor):
    """Создание таблицы purchases на основе shopping с дополнительными полями"""
    
    # Проверяем, существует ли таблица purchases
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'purchases'
        );
    """)
    result = cursor.fetchone()
    # result может быть кортежем или словарем в зависимости от курсора
    if hasattr(result, 'keys'):  # RealDictCursor
        purchases_exists = result['exists'] if result else False
    else:  # обычный курсор
        purchases_exists = result[0] if result else False
    
    if not purchases_exists:
        print("📦 Создаем таблицу purchases...")
        
        # Создаем таблицу purchases на основе shopping
        cursor.execute("""
            CREATE TABLE purchases AS 
            SELECT 
                id,
                user_id,
                project_id,
                item as name,
                quantity,
                CASE 
                    WHEN status = 'Куплено' THEN true 
                    ELSE false 
                END as completed,
                created_at,
                NULL::DECIMAL as price,
                'other'::TEXT as category
            FROM shopping;
        """)
        
        # Добавляем первичный ключ и ограничения
        cursor.execute("ALTER TABLE purchases ADD PRIMARY KEY (id);")
        cursor.execute("ALTER TABLE purchases ALTER COLUMN name SET NOT NULL;")
        cursor.execute("ALTER TABLE purchases ALTER COLUMN quantity SET NOT NULL;")
        cursor.execute("ALTER TABLE purchases ALTER COLUMN completed SET DEFAULT false;")
        
        # Создаем индексы
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_purchases_user_id ON purchases(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_purchases_completed ON purchases(completed);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_purchases_category ON purchases(category);")
        
        print("✅ Таблица purchases создана")
    else:
        print("ℹ️ Таблица purchases уже существует")

def migration_20241220_120003_default_user_settings(cursor):
    """Добавление настроек по умолчанию для всех пользователей"""
    
    # Получаем всех пользователей без настроек темы
    cursor.execute("""
        SELECT DISTINCT u.user_id 
        FROM users u 
        LEFT JOIN user_settings us ON u.user_id = us.user_id AND us.key = 'theme'
        WHERE us.user_id IS NULL;
    """)
    users_without_theme = cursor.fetchall()
    
    for user in users_without_theme:
        # user может быть кортежем или словарем в зависимости от курсора
        if hasattr(user, 'keys'):  # RealDictCursor
            user_id = user['user_id']
        else:  # обычный курсор
            user_id = user[0]
        
        # Добавляем настройки по умолчанию
        cursor.execute("""
            INSERT INTO user_settings (user_id, key, value) 
            VALUES (%s, 'theme', 'auto')
            ON CONFLICT (user_id, key) DO NOTHING;
        """, (user_id,))
        
        cursor.execute("""
            INSERT INTO user_settings (user_id, key, value) 
            VALUES (%s, 'email_notifications', 'false')
            ON CONFLICT (user_id, key) DO NOTHING;
        """, (user_id,))
        
        cursor.execute("""
            INSERT INTO user_settings (user_id, key, value) 
            VALUES (%s, 'task_reminders', 'true')
            ON CONFLICT (user_id, key) DO NOTHING;
        """, (user_id,))
        
        cursor.execute("""
            INSERT INTO user_settings (user_id, key, value) 
            VALUES (%s, 'timezone', 'Europe/Moscow')
            ON CONFLICT (user_id, key) DO NOTHING;
        """, (user_id,))
    
    if users_without_theme:
        print(f"✅ Добавлены настройки для {len(users_without_theme)} пользователей")
    else:
        print("ℹ️ Все пользователи уже имеют настройки")

def migration_20241220_120004_add_completed_at_field(cursor):
    """Добавление поля completed_at в таблицу tasks"""
    
    # Проверяем, есть ли уже поле completed_at
    cursor.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'tasks' AND column_name = 'completed_at';
    """)
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE tasks ADD COLUMN completed_at TEXT;")
        print("✅ Добавлено поле completed_at в tasks")
    else:
        print("ℹ️ Поле completed_at уже существует")

def migration_20241220_120006_create_shopping_lists_table(cursor):
    """Создание таблицы shopping_lists и обновление таблицы purchases"""
    
    # Создаем таблицу списков покупок
    print("📋 Создаем таблицу shopping_lists...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shopping_lists (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            project_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)
    
    # Создаем индексы
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_shopping_lists_user_id ON shopping_lists(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_shopping_lists_project_id ON shopping_lists(project_id);")
    
    # Проверяем, существует ли столбец shopping_list_id в таблице purchases
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'purchases' AND column_name = 'shopping_list_id';
    """)
    column_exists = cursor.fetchone()
    
    if not column_exists:
        print("🔗 Добавляем связь со списками в таблицу purchases...")
        # Добавляем столбец для связи со списком покупок
        cursor.execute("""
            ALTER TABLE purchases 
            ADD COLUMN shopping_list_id INTEGER,
            ADD COLUMN url TEXT,
            ADD COLUMN comment TEXT;
        """)
        
        # Добавляем внешний ключ
        cursor.execute("""
            ALTER TABLE purchases 
            ADD CONSTRAINT fk_purchases_shopping_list 
            FOREIGN KEY (shopping_list_id) REFERENCES shopping_lists(id) ON DELETE SET NULL;
        """)
        
        # Создаем индекс
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_purchases_shopping_list_id ON purchases(shopping_list_id);")
    
    # Создаем дефолтный список для существующих покупок
    print("📝 Создаем дефолтные списки для существующих пользователей...")
    cursor.execute("""
        INSERT INTO shopping_lists (name, project_id, user_id, created_at)
        SELECT DISTINCT 
            'Общий список' as name,
            COALESCE(p.project_id, (
                SELECT id FROM projects 
                WHERE owner_id = p.user_id 
                ORDER BY created_at ASC 
                LIMIT 1
            )) as project_id,
            p.user_id,
            CURRENT_TIMESTAMP
        FROM purchases p
        WHERE NOT EXISTS (
            SELECT 1 FROM shopping_lists sl 
            WHERE sl.user_id = p.user_id
        )
        AND p.user_id IS NOT NULL;
    """)
    
    # Привязываем существующие покупки к дефолтному списку
    cursor.execute("""
        UPDATE purchases 
        SET shopping_list_id = (
            SELECT sl.id 
            FROM shopping_lists sl 
            WHERE sl.user_id = purchases.user_id 
            AND sl.name = 'Общий список'
            LIMIT 1
        )
        WHERE shopping_list_id IS NULL;
    """)
    
    print("✅ Таблица shopping_lists создана и настроена")

# === ОСНОВНАЯ ЛОГИКА ===

MIGRATIONS = [
    ('20241220_120000', 'initial_schema', migration_20241220_120000_initial_schema),
    ('20241220_120001', 'add_extended_fields', migration_20241220_120001_add_extended_fields),
    ('20241220_120002', 'create_purchases_table', migration_20241220_120002_create_purchases_table),
    ('20241220_120003', 'default_user_settings', migration_20241220_120003_default_user_settings),
    ('20241220_120004', 'add_completed_at_field', migration_20241220_120004_add_completed_at_field),
    ('20241220_120006', 'create_shopping_lists_table', migration_20241220_120006_create_shopping_lists_table),
]

def run_migrations():
    """Выполнить все неприменённые миграции"""
    print("🚀 Запуск миграций на сервере NetAngels...")
    
    # Проверяем подключение к БД
    try:
        with get_conn() as conn:
            print("✅ Подключение к базе данных установлено")
    except Exception as e:
        print(f"❌ Не удалось подключиться к базе данных: {e}")
        return False
    
    # Создаем таблицу миграций
    ensure_migrations_table()
    
    # Получаем список выполненных миграций
    executed = set(get_executed_migrations())
    print(f"📋 Выполнено миграций: {len(executed)}")
    
    # Выполняем неприменённые миграции
    success_count = 0
    for version, name, migration_func in MIGRATIONS:
        if version not in executed:
            if execute_migration(version, name, migration_func):
                success_count += 1
            else:
                print(f"❌ Остановка на миграции {version}")
                return False
        else:
            print(f"✅ Миграция {version} уже выполнена")
    
    total_pending = len([m for m in MIGRATIONS if m[0] not in executed])
    
    if total_pending == 0:
        print("✅ Все миграции уже применены")
    else:
        print(f"🎉 Выполнено {success_count} новых миграций!")
    
    return True

def show_status():
    """Показать статус миграций"""
    print("📊 Статус миграций на сервере:")
    
    try:
        executed = set(get_executed_migrations())
        print(f"   Всего доступно: {len(MIGRATIONS)}")
        print(f"   Выполнено: {len(executed)}")
        print(f"   Ожидает выполнения: {len(MIGRATIONS) - len(executed)}")
        
        print("\n📋 Все миграции:")
        for version, name, _ in MIGRATIONS:
            status = "✅" if version in executed else "❌"
            print(f"   {status} {version}: {name}")
            
    except Exception as e:
        print(f"❌ Ошибка получения статуса: {e}")

def main():
    """Главная функция"""
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python server_migrate.py migrate  - выполнить все миграции")
        print("  python server_migrate.py status   - показать статус")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "migrate":
        success = run_migrations()
        if success:
            print("\n🎉 Миграции завершены! Сервер готов к работе.")
        sys.exit(0 if success else 1)
    elif command == "status":
        show_status()
    else:
        print(f"❌ Неизвестная команда: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()