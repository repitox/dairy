#!/usr/bin/env python3
"""
Миграция: Добавление уникального ограничения в таблицу project_members
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

def check_constraint_exists(conn):
    """Проверить, существует ли уникальное ограничение"""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = 'project_members' 
            AND constraint_type = 'UNIQUE'
            AND constraint_name LIKE '%project_id%user_id%'
        """)
        return cur.fetchone() is not None

def add_unique_constraint(conn):
    """Добавить уникальное ограничение в таблицу project_members"""
    with conn.cursor() as cur:
        print("🔧 Добавляем уникальное ограничение в таблицу project_members...")
        
        # Сначала удаляем дубликаты, если они есть
        print("🧹 Удаляем возможные дубликаты...")
        cur.execute("""
            DELETE FROM project_members 
            WHERE id NOT IN (
                SELECT MIN(id) 
                FROM project_members 
                GROUP BY project_id, user_id
            )
        """)
        deleted_count = cur.rowcount
        if deleted_count > 0:
            print(f"🗑️ Удалено {deleted_count} дубликатов")
        else:
            print("✅ Дубликатов не найдено")
        
        # Добавляем уникальное ограничение
        cur.execute("""
            ALTER TABLE project_members 
            ADD CONSTRAINT unique_project_user 
            UNIQUE (project_id, user_id)
        """)
        
        print("✅ Уникальное ограничение добавлено успешно")
        
        # Проверяем результат
        cur.execute("""
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints 
            WHERE table_name = 'project_members' 
            AND constraint_name = 'unique_project_user'
        """)
        result = cur.fetchone()
        if result:
            print(f"📊 Ограничение создано: {result[0]} ({result[1]})")
        
        conn.commit()

def main():
    """Основная функция миграции"""
    print("🚀 Запуск миграции: добавление уникального ограничения в project_members")
    print(f"⏰ Время: {datetime.now().isoformat()}")
    
    try:
        # Подключаемся к БД
        conn = get_db_connection()
        print("✅ Подключение к БД установлено")
        
        # Проверяем текущие ограничения
        print("\n📋 Текущие ограничения таблицы project_members:")
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT constraint_name, constraint_type
                FROM information_schema.table_constraints 
                WHERE table_name = 'project_members' 
                ORDER BY constraint_name
            """)
            for row in cur.fetchall():
                print(f"  - {row['constraint_name']}: {row['constraint_type']}")
        
        # Проверяем, нужна ли миграция
        if check_constraint_exists(conn):
            print("\n⚠️ Уникальное ограничение уже существует, миграция не требуется")
        else:
            print("\n🔧 Уникальное ограничение не найдено, выполняем миграцию...")
            add_unique_constraint(conn)
            print("\n🎉 Миграция выполнена успешно!")
        
        # Показываем финальные ограничения
        print("\n📋 Финальные ограничения таблицы project_members:")
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT constraint_name, constraint_type
                FROM information_schema.table_constraints 
                WHERE table_name = 'project_members' 
                ORDER BY constraint_name
            """)
            for row in cur.fetchall():
                print(f"  - {row['constraint_name']}: {row['constraint_type']}")
        
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