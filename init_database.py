"""
Универсальная инициализация базы данных
Автоматически создает все необходимые таблицы при запуске проекта
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

def get_database_connection():
    """Получить подключение к базе данных"""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise Exception("DATABASE_URL не установлен")
    return psycopg2.connect(db_url, cursor_factory=RealDictCursor)

def table_exists(cursor, table_name):
    """Проверить, существует ли таблица"""
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = %s
        );
    """, (table_name,))
    result = cursor.fetchone()
    return result['exists'] if result else False

def column_exists(cursor, table_name, column_name):
    """Проверить, существует ли колонка в таблице"""
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = %s AND column_name = %s
        );
    """, (table_name, column_name))
    result = cursor.fetchone()
    return result['exists'] if result else False

def create_purchases_table(cursor):
    """Создать таблицу purchases на основе shopping"""
    if not table_exists(cursor, 'purchases'):
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
                'other'::TEXT as category,
                NULL::INTEGER as shopping_list_id,
                NULL::TEXT as url,
                NULL::TEXT as comment
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
        
        # Проверяем и добавляем недостающие колонки
        if not column_exists(cursor, 'purchases', 'shopping_list_id'):
            cursor.execute("ALTER TABLE purchases ADD COLUMN shopping_list_id INTEGER")
            print("✅ Добавлена колонка shopping_list_id")
        
        if not column_exists(cursor, 'purchases', 'url'):
            cursor.execute("ALTER TABLE purchases ADD COLUMN url TEXT")
            print("✅ Добавлена колонка url")
            
        if not column_exists(cursor, 'purchases', 'comment'):
            cursor.execute("ALTER TABLE purchases ADD COLUMN comment TEXT")
            print("✅ Добавлена колонка comment")

def create_shopping_lists_table(cursor):
    """Создать таблицу shopping_lists"""
    if not table_exists(cursor, 'shopping_lists'):
        print("📋 Создаем таблицу shopping_lists...")
        
        cursor.execute("""
            CREATE TABLE shopping_lists (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                project_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Создаем индексы
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_shopping_lists_user_id ON shopping_lists(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_shopping_lists_project_id ON shopping_lists(project_id);")
        
        print("✅ Таблица shopping_lists создана")
    else:
        print("ℹ️ Таблица shopping_lists уже существует")

def create_notes_table(cursor):
    """Создать таблицу notes, если её нет"""
    if not table_exists(cursor, 'notes'):
        print("📝 Создаем таблицу notes...")
        
        cursor.execute("""
            CREATE TABLE notes (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Создаем индексы
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_user_id ON notes(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_created_at ON notes(created_at);")
        
        print("✅ Таблица notes создана")
    else:
        print("ℹ️ Таблица notes уже существует")

def create_events_table(cursor):
    """Создать таблицу events, если её нет"""
    if not table_exists(cursor, 'events'):
        print("📅 Создаем таблицу events...")
        
        cursor.execute("""
            CREATE TABLE events (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                project_id INTEGER,
                title TEXT NOT NULL,
                location TEXT,
                start_at TEXT,
                end_at TEXT,
                active BOOLEAN DEFAULT TRUE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            );
        """)
        
        # Создаем индексы
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_start_at ON events(start_at);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_active ON events(active);")
        
        print("✅ Таблица events создана")
    else:
        print("ℹ️ Таблица events уже существует")

def initialize_database():
    """Основная функция инициализации базы данных"""
    try:
        print(f"🚀 Инициализация базы данных - {datetime.now().isoformat()}")
        
        with get_database_connection() as conn:
            with conn.cursor() as cur:
                # Создаем все необходимые таблицы
                create_purchases_table(cur)
                create_shopping_lists_table(cur)
                create_notes_table(cur)
                create_events_table(cur)
                
                conn.commit()
                print("✅ Инициализация базы данных завершена успешно")
                
    except Exception as e:
        print(f"❌ Ошибка инициализации базы данных: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    initialize_database()