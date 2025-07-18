#!/usr/bin/env python3
"""
Проверка продакшн БД на NetAngels
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Настройки подключения к БД NetAngels
DB_CONFIG = {
    'host': 'postgres.c107597.h2',
    'database': 'c107597_rptx_na4u_ru',
    'user': 'c107597_rptx_na4u_ru',
    'password': 'ZiKceXoydixol93',
    'port': 5432
}

def main():
    try:
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        
        with conn.cursor() as cur:
            print("🔗 Подключение к продакшн БД успешно!")
            print()
            
            # Список всех таблиц
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
            tables = cur.fetchall()
            print(f"📋 Таблицы в продакшн БД ({len(tables)} шт.):")
            for table in tables:
                print(f"   - {table['table_name']}")
            print()
            
            # Проверяем статус миграций
            cur.execute("SELECT version, name, executed_at FROM schema_migrations ORDER BY executed_at")
            migrations = cur.fetchall()
            print(f"🔄 Выполненные миграции ({len(migrations)} шт.):")
            for m in migrations:
                print(f"   ✅ {m['version']}: {m['name']} ({m['executed_at']})")
            print()
            
            # Проверяем структуру таблицы tasks
            cur.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'tasks'
                ORDER BY ordinal_position
            """)
            columns = cur.fetchall()
            print(f"📊 Структура таблицы tasks ({len(columns)} полей):")
            for col in columns:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                print(f"   - {col['column_name']}: {col['data_type']} {nullable}{default}")
            print()
            
            # Количество записей в основных таблицах
            tables_to_check = ['users', 'projects', 'tasks', 'events', 'shopping', 'purchases', 'user_settings', 'project_members', 'logs', 'reminder_logs']
            print("📈 Количество записей:")
            total_records = 0
            for table in tables_to_check:
                try:
                    cur.execute(f"SELECT COUNT(*) as count FROM {table}")
                    count = cur.fetchone()['count']
                    total_records += count
                    print(f"   - {table}: {count} записей")
                except Exception as e:
                    print(f"   - {table}: ошибка ({e})")
            
            print(f"\n📊 Всего записей в БД: {total_records}")
            
            # Проверяем последние задачи
            cur.execute("SELECT id, title, completed, created_at FROM tasks ORDER BY id DESC LIMIT 5")
            recent_tasks = cur.fetchall()
            if recent_tasks:
                print(f"\n📝 Последние задачи ({len(recent_tasks)} шт.):")
                for task in recent_tasks:
                    status = "✅" if task['completed'] else "❌"
                    print(f"   {status} #{task['id']}: {task['title']} ({task['created_at']})")
            
            # Проверяем последние события
            cur.execute("SELECT id, title, start_at FROM events ORDER BY id DESC LIMIT 3")
            recent_events = cur.fetchall()
            if recent_events:
                print(f"\n📅 Последние события ({len(recent_events)} шт.):")
                for event in recent_events:
                    print(f"   📅 #{event['id']}: {event['title']} ({event['start_at']})")
        
        conn.close()
        print("\n✅ Проверка завершена успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")

if __name__ == "__main__":
    main()