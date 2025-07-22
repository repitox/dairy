#!/usr/bin/env python3
"""
Миграция: Добавление колонки 'active' в таблицу projects
"""

import psycopg2
import psycopg2.extras
import os
from datetime import datetime

def get_db_connection():
    """Получить подключение к БД"""
    # Определяем, локальная это среда или продакшн
    if os.path.exists('/.dockerenv'):
        # Docker среда (локальная разработка)
        return psycopg2.connect(
            host="db",
            database="telegram_app",
            user="postgres",
            password="postgres",
            port=5432
        )
    else:
        # Продакшн среда NetAngels
        return psycopg2.connect(
            host='postgres.c107597.h2',
            database='c107597_rptx_na4u_ru',
            user='c107597_rptx_na4u_ru',
            password='ZiKceXoydixol93',
            port=5432
        )

def check_column_exists(conn):
    """Проверить, существует ли колонка active в таблице projects"""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'projects' AND column_name = 'active'
        """)
        return cur.fetchone() is not None

def add_active_column(conn):
    """Добавить колонку active в таблицу projects"""
    with conn.cursor() as cur:
        print("🔧 Добавляем колонку 'active' в таблицу projects...")
        
        # Добавляем колонку с значением по умолчанию TRUE
        cur.execute("""
            ALTER TABLE projects 
            ADD COLUMN active BOOLEAN DEFAULT TRUE NOT NULL
        """)
        
        print("✅ Колонка 'active' добавлена успешно")
        
        # Проверяем результат
        cur.execute("""
            SELECT column_name, data_type, column_default, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'projects' AND column_name = 'active'
        """)
        result = cur.fetchone()
        if result:
            print(f"📊 Колонка создана: {result[0]} ({result[1]}, default: {result[2]}, nullable: {result[3]})")
        
        conn.commit()

def main():
    """Основная функция миграции"""
    print("🚀 Запуск миграции: добавление колонки 'active' в таблицу projects")
    print(f"⏰ Время: {datetime.now().isoformat()}")
    
    try:
        # Подключаемся к БД
        conn = get_db_connection()
        print("✅ Подключение к БД установлено")
        
        # Проверяем текущую структуру
        print("\n📋 Текущая структура таблицы projects:")
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT column_name, data_type, column_default, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'projects' 
                ORDER BY ordinal_position
            """)
            for row in cur.fetchall():
                print(f"  - {row['column_name']}: {row['data_type']} (default: {row['column_default']}, nullable: {row['is_nullable']})")
        
        # Проверяем, нужна ли миграция
        if check_column_exists(conn):
            print("\n⚠️ Колонка 'active' уже существует, миграция не требуется")
        else:
            print("\n🔧 Колонка 'active' не найдена, выполняем миграцию...")
            add_active_column(conn)
            print("\n🎉 Миграция выполнена успешно!")
        
        # Показываем финальную структуру
        print("\n📋 Финальная структура таблицы projects:")
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT column_name, data_type, column_default, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'projects' 
                ORDER BY ordinal_position
            """)
            for row in cur.fetchall():
                print(f"  - {row['column_name']}: {row['data_type']} (default: {row['column_default']}, nullable: {row['is_nullable']})")
        
        conn.close()
        print("\n✅ Миграция завершена успешно")
        
    except Exception as e:
        print(f"\n❌ Ошибка миграции: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)