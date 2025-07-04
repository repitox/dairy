#!/usr/bin/env python3
"""
Миграция для добавления поля completed_at в таблицу tasks
"""

import psycopg2
import os
from datetime import datetime

def migrate():
    # Подключение к базе данных
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'db'),
        database=os.getenv('DB_NAME', 'telegram_app'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'password'),
        port=os.getenv('DB_PORT', '5432')
    )
    
    try:
        with conn.cursor() as cur:
            # Проверяем, существует ли уже поле completed_at
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'tasks' AND column_name = 'completed_at'
            """)
            
            if cur.fetchone() is None:
                print("Добавляем поле completed_at в таблицу tasks...")
                
                # Добавляем поле completed_at
                cur.execute("ALTER TABLE tasks ADD COLUMN completed_at TEXT")
                
                # Для уже завершенных задач устанавливаем completed_at = created_at
                cur.execute("""
                    UPDATE tasks 
                    SET completed_at = created_at 
                    WHERE completed = TRUE AND completed_at IS NULL
                """)
                
                conn.commit()
                print("✅ Миграция completed_at выполнена успешно")
            else:
                print("ℹ️ Поле completed_at уже существует")
                
    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()