#!/usr/bin/env python3
"""
🚀 Выполнение недостающих миграций в продакшене
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Настройки продакшен БД
DB_CONFIG = {
    'host': 'postgres.c107597.h2',
    'database': 'c107597_rptx_na4u_ru',
    'user': 'c107597_rptx_na4u_ru',
    'password': 'ZiKceXoydixol93',
    'port': 5432
}

def run_migration_20241220_120005(cursor):
    """Создание таблицы заметок"""
    print("🔄 Выполняем миграцию 20241220_120005_create_notes_table...")
    
    # Заметки
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Индекс для быстрого поиска заметок пользователя
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_notes_user_id ON notes(user_id);
    """)
    
    # Индекс для сортировки по дате создания
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_notes_created_at ON notes(created_at DESC);
    """)
    
    # Записываем миграцию в таблицу
    cursor.execute("""
        INSERT INTO schema_migrations (version, name, executed_at) 
        VALUES (%s, %s, %s);
    """, ('20241220_120005', 'create_notes_table', datetime.now().isoformat()))
    
    print("✅ Миграция 20241220_120005 выполнена")

def run_migration_20241220_120006(cursor):
    """Создание таблицы shopping_lists"""
    print("🔄 Выполняем миграцию 20241220_120006_create_shopping_lists_table...")
    
    # Создаем таблицу списков покупок
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shopping_lists (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            project_id INTEGER NOT NULL,
            user_id BIGINT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
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
    
    # Записываем миграцию в таблицу
    cursor.execute("""
        INSERT INTO schema_migrations (version, name, executed_at) 
        VALUES (%s, %s, %s);
    """, ('20241220_120006', 'create_shopping_lists_table', datetime.now().isoformat()))
    
    print("✅ Миграция 20241220_120006 выполнена")

def run_missing_migrations():
    try:
        print("🔗 Подключаемся к продакшен БД...")
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        
        print('✅ Подключение успешно!')
        
        # Проверяем, какие миграции уже выполнены
        cur.execute('SELECT version FROM schema_migrations ORDER BY version;')
        executed_migrations = [row['version'] for row in cur.fetchall()]
        
        print(f'📋 Выполненные миграции: {executed_migrations}')
        
        # Выполняем недостающие миграции
        if '20241220_120005' not in executed_migrations:
            run_migration_20241220_120005(cur)
            conn.commit()
        else:
            print('⏭️ Миграция 20241220_120005 уже выполнена')
        
        if '20241220_120006' not in executed_migrations:
            run_migration_20241220_120006(cur)
            conn.commit()
        else:
            print('⏭️ Миграция 20241220_120006 уже выполнена')
        
        # Проверяем финальное состояние
        print('\n🔍 ФИНАЛЬНОЕ СОСТОЯНИЕ БД:')
        print('=' * 50)
        
        cur.execute('SELECT table_name FROM information_schema.tables WHERE table_schema = \'public\' ORDER BY table_name;')
        tables = cur.fetchall()
        
        print('📋 Таблицы:')
        for table in tables:
            print(f'  - {table["table_name"]}')
        
        print('\n🔄 Миграции:')
        cur.execute('SELECT version, name, executed_at FROM schema_migrations ORDER BY version;')
        migrations = cur.fetchall()
        for migration in migrations:
            print(f'  ✅ {migration["version"]} - {migration["name"]} ({migration["executed_at"]})')
        
        cur.close()
        conn.close()
        print('\n✅ Все миграции выполнены успешно!')
        
    except Exception as e:
        print(f'❌ Ошибка: {e}')
        if 'conn' in locals():
            conn.rollback()

if __name__ == '__main__':
    run_missing_migrations()