#!/usr/bin/env python3
"""
🔍 Проверка продакшен БД через SSH туннель
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import time

# Настройки продакшен БД через SSH туннель
DB_CONFIG = {
    'host': 'localhost',  # Через SSH туннель
    'database': 'c107597_rptx_na4u_ru',
    'user': 'c107597_rptx_na4u_ru',
    'password': 'ZiKceXoydixol93',
    'port': 5433  # Локальный порт SSH туннеля
}

def check_production_schema():
    print("🔗 Подключаемся к продакшен БД через SSH туннель...")
    print("⏳ Ждем установки туннеля...")
    time.sleep(2)  # Даем время на установку туннеля
    
    try:
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        
        print('✅ Подключение успешно!')
        print('\n🔍 СХЕМА БД В ПРОДАКШЕНЕ:')
        print('=' * 60)
        
        # Получаем все таблицы
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        
        if not tables:
            print("❌ Таблицы не найдены!")
            return
        
        schema_info = {}
        
        for table in tables:
            table_name = table['table_name']
            print(f'\n📋 Таблица: {table_name}')
            
            # Получаем структуру таблицы
            cur.execute("""
                SELECT 
                    column_name, 
                    data_type, 
                    is_nullable,
                    column_default,
                    character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position;
            """, (table_name,))
            
            columns = cur.fetchall()
            schema_info[table_name] = columns
            
            for col in columns:
                nullable = 'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'
                default = f' DEFAULT {col["column_default"]}' if col['column_default'] else ''
                length = f'({col["character_maximum_length"]})' if col['character_maximum_length'] else ''
                print(f'  - {col["column_name"]}: {col["data_type"]}{length} {nullable}{default}')
        
        # Проверяем выполненные миграции
        print('\n🔄 ВЫПОЛНЕННЫЕ МИГРАЦИИ:')
        print('=' * 60)
        try:
            cur.execute('SELECT version, name, executed_at FROM schema_migrations ORDER BY version;')
            migrations = cur.fetchall()
            if migrations:
                for migration in migrations:
                    print(f'✅ {migration["version"]} - {migration["name"]} ({migration["executed_at"]})')
            else:
                print('❌ Миграции не найдены!')
        except Exception as e:
            print(f'❌ Таблица schema_migrations не существует: {e}')
        
        # Проверяем количество записей в основных таблицах
        print('\n📊 СТАТИСТИКА:')
        print('=' * 60)
        
        main_tables = ['users', 'projects', 'tasks', 'events', 'shopping', 'purchases', 'notes', 'shopping_lists']
        for table_name in main_tables:
            if table_name in schema_info:
                try:
                    cur.execute(f'SELECT COUNT(*) as count FROM {table_name};')
                    count = cur.fetchone()['count']
                    print(f'{table_name}: {count} записей')
                except Exception as e:
                    print(f'{table_name}: ошибка - {e}')
        
        # Проверяем последние записи в основных таблицах
        print('\n📝 ПОСЛЕДНИЕ ЗАПИСИ:')
        print('=' * 60)
        
        if 'tasks' in schema_info:
            try:
                cur.execute('SELECT id, title, user_id, completed FROM tasks ORDER BY id DESC LIMIT 3;')
                tasks = cur.fetchall()
                print('\n📋 Последние задачи:')
                for task in tasks:
                    status = '✅' if task['completed'] else '⏳'
                    print(f'  {status} ID:{task["id"]} - {task["title"]} (user: {task["user_id"]})')
            except Exception as e:
                print(f'Ошибка при получении задач: {e}')
        
        if 'users' in schema_info:
            try:
                cur.execute('SELECT user_id, first_name, username FROM users ORDER BY user_id DESC LIMIT 3;')
                users = cur.fetchall()
                print('\n👥 Последние пользователи:')
                for user in users:
                    print(f'  👤 ID:{user["user_id"]} - {user["first_name"]} (@{user["username"]})')
            except Exception as e:
                print(f'Ошибка при получении пользователей: {e}')
        
        cur.close()
        conn.close()
        print('\n✅ Проверка завершена!')
        
    except Exception as e:
        print(f'❌ Ошибка подключения: {e}')
        print(f'Тип ошибки: {type(e).__name__}')

if __name__ == '__main__':
    check_production_schema()