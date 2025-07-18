#!/usr/bin/env python3
"""
🔍 Скрипт для проверки схемы БД в продакшене
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Настройки продакшен БД
DB_CONFIG = {
    'host': 'postgres.c107597.h2',
    'database': 'c107597_rptx_na4u_ru',
    'user': 'c107597_rptx_na4u_ru',
    'password': 'ZiKceXoydixol93',
    'port': 5432
}

def check_schema():
    try:
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        
        print('🔍 СХЕМА БД В ПРОДАКШЕНЕ:')
        print('=' * 50)
        
        # Получаем все таблицы
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        
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
                    column_default
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position;
            """, (table_name,))
            
            columns = cur.fetchall()
            schema_info[table_name] = columns
            
            for col in columns:
                nullable = 'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'
                default = f' DEFAULT {col["column_default"]}' if col['column_default'] else ''
                print(f'  - {col["column_name"]}: {col["data_type"]} {nullable}{default}')
        
        # Проверяем выполненные миграции
        print('\n🔄 ВЫПОЛНЕННЫЕ МИГРАЦИИ:')
        print('=' * 50)
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
        print('=' * 50)
        
        main_tables = ['users', 'projects', 'tasks', 'events', 'shopping', 'purchases']
        for table_name in main_tables:
            if table_name in schema_info:
                try:
                    cur.execute(f'SELECT COUNT(*) as count FROM {table_name};')
                    count = cur.fetchone()['count']
                    print(f'{table_name}: {count} записей')
                except Exception as e:
                    print(f'{table_name}: ошибка - {e}')
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f'❌ Ошибка подключения: {e}')

if __name__ == '__main__':
    check_schema()