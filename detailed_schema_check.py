#!/usr/bin/env python3
"""
🔍 Детальная проверка схемы продакшен БД
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

def detailed_schema_check():
    try:
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        
        print('🔍 ДЕТАЛЬНАЯ ПРОВЕРКА СХЕМЫ ПРОДАКШЕН БД:')
        print('=' * 60)
        
        # Проверяем структуру таблицы notes
        print('\n📋 Структура таблицы notes:')
        cur.execute("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'notes' ORDER BY ordinal_position;")
        notes_columns = cur.fetchall()
        for col in notes_columns:
            nullable = 'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'
            print(f'  - {col["column_name"]}: {col["data_type"]} {nullable}')
        
        # Проверяем структуру таблицы shopping_lists
        print('\n📋 Структура таблицы shopping_lists:')
        cur.execute("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'shopping_lists' ORDER BY ordinal_position;")
        shopping_lists_columns = cur.fetchall()
        for col in shopping_lists_columns:
            nullable = 'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'
            print(f'  - {col["column_name"]}: {col["data_type"]} {nullable}')
        
        # Проверяем обновленную структуру таблицы purchases
        print('\n📋 Структура таблицы purchases:')
        cur.execute("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'purchases' ORDER BY ordinal_position;")
        purchases_columns = cur.fetchall()
        for col in purchases_columns:
            nullable = 'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'
            print(f'  - {col["column_name"]}: {col["data_type"]} {nullable}')
        
        # Проверяем количество записей
        print('\n📊 СТАТИСТИКА:')
        tables = ['users', 'projects', 'tasks', 'events', 'shopping', 'purchases', 'notes', 'shopping_lists']
        for table_name in tables:
            try:
                cur.execute(f'SELECT COUNT(*) as count FROM {table_name};')
                count = cur.fetchone()['count']
                print(f'{table_name}: {count} записей')
            except Exception as e:
                print(f'{table_name}: ошибка - {e}')
        
        # Проверяем индексы для новых таблиц
        print('\n🔍 ИНДЕКСЫ:')
        cur.execute("""
            SELECT tablename, indexname, indexdef 
            FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND tablename IN ('notes', 'shopping_lists', 'purchases')
            ORDER BY tablename, indexname;
        """)
        indexes = cur.fetchall()
        
        current_table = None
        for idx in indexes:
            if idx['tablename'] != current_table:
                current_table = idx['tablename']
                print(f'\n📋 {current_table}:')
            print(f'  - {idx["indexname"]}: {idx["indexdef"]}')
        
        cur.close()
        conn.close()
        print('\n✅ Детальная проверка завершена!')
        
    except Exception as e:
        print(f'❌ Ошибка: {e}')

if __name__ == '__main__':
    detailed_schema_check()