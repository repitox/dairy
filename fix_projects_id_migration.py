#!/usr/bin/env python3
"""
Миграция: Исправление поля id в таблице projects (добавление автоинкремента)
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

def fix_projects_id(conn):
    """Исправить поле id в таблице projects"""
    with conn.cursor() as cur:
        print("🔧 Исправляем поле id в таблице projects...")
        
        # 1. Создаем последовательность
        print("📊 Создаем последовательность projects_id_seq...")
        cur.execute("CREATE SEQUENCE IF NOT EXISTS projects_id_seq")
        
        # 2. Находим максимальный ID (исключая NULL)
        cur.execute("SELECT COALESCE(MAX(id), 0) FROM projects WHERE id IS NOT NULL")
        max_id = cur.fetchone()[0]
        print(f"📈 Максимальный существующий ID: {max_id}")
        
        # 3. Устанавливаем начальное значение последовательности
        if max_id > 0:
            cur.execute(f"SELECT setval('projects_id_seq', {max_id})")
            print(f"🔢 Последовательность установлена на {max_id}")
        
        # 4. Обновляем записи с NULL id
        cur.execute("SELECT COUNT(*) FROM projects WHERE id IS NULL")
        null_count = cur.fetchone()[0]
        print(f"🔍 Найдено записей с NULL id: {null_count}")
        
        if null_count > 0:
            # Обновляем NULL записи, присваивая им новые ID из последовательности
            cur.execute("""
                UPDATE projects 
                SET id = nextval('projects_id_seq') 
                WHERE id IS NULL
            """)
            print(f"✅ Обновлено {null_count} записей с NULL id")
        
        # 5. Устанавливаем default значение для поля id
        cur.execute("""
            ALTER TABLE projects 
            ALTER COLUMN id SET DEFAULT nextval('projects_id_seq')
        """)
        print("✅ Установлено default значение для поля id")
        
        # 6. Делаем поле id NOT NULL
        cur.execute("ALTER TABLE projects ALTER COLUMN id SET NOT NULL")
        print("✅ Поле id теперь NOT NULL")
        
        # 7. Создаем первичный ключ, если его нет
        try:
            cur.execute("ALTER TABLE projects ADD PRIMARY KEY (id)")
            print("✅ Добавлен первичный ключ")
        except psycopg2.errors.DuplicateObject:
            print("ℹ️ Первичный ключ уже существует")
        except Exception as e:
            print(f"⚠️ Не удалось добавить первичный ключ: {e}")
        
        conn.commit()
        print("✅ Исправление поля id завершено")

def main():
    """Основная функция миграции"""
    print("🚀 Запуск миграции: исправление поля id в таблице projects")
    print(f"⏰ Время: {datetime.now().isoformat()}")
    
    try:
        # Подключаемся к БД
        conn = get_db_connection()
        print("✅ Подключение к БД установлено")
        
        # Проверяем текущую структуру
        print("\n📋 Текущая структура поля id:")
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT column_name, data_type, column_default, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'projects' AND column_name = 'id'
            """)
            row = cur.fetchone()
            if row:
                print(f"  - {row['column_name']}: {row['data_type']} (default: {row['column_default']}, nullable: {row['is_nullable']})")
            
            # Проверяем количество записей с NULL id
            cur.execute("SELECT COUNT(*) as total, COUNT(id) as with_id FROM projects")
            counts = cur.fetchone()
            print(f"  - Всего записей: {counts['total']}, с ID: {counts['with_id']}, без ID: {counts['total'] - counts['with_id']}")
        
        # Выполняем исправление
        print("\n🔧 Выполняем исправление...")
        fix_projects_id(conn)
        
        # Показываем финальную структуру
        print("\n📋 Финальная структура поля id:")
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT column_name, data_type, column_default, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'projects' AND column_name = 'id'
            """)
            row = cur.fetchone()
            if row:
                print(f"  - {row['column_name']}: {row['data_type']} (default: {row['column_default']}, nullable: {row['is_nullable']})")
            
            # Проверяем записи после исправления
            cur.execute("SELECT COUNT(*) as total, COUNT(id) as with_id FROM projects")
            counts = cur.fetchone()
            print(f"  - Всего записей: {counts['total']}, с ID: {counts['with_id']}, без ID: {counts['total'] - counts['with_id']}")
            
            # Показываем несколько примеров
            cur.execute("SELECT id, name, owner_id FROM projects LIMIT 5")
            print("\n📊 Примеры записей:")
            for row in cur.fetchall():
                print(f"  - ID: {row['id']}, Name: {row['name']}, Owner: {row['owner_id']}")
        
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