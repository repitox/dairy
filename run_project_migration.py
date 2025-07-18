#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import get_conn

def run_migration():
    """Запускает миграцию для добавления поля active в таблицу projects"""
    print("🔄 Запуск миграции для добавления поля active...")
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Добавляем поле active со значением по умолчанию TRUE
                cur.execute("""
                    ALTER TABLE projects 
                    ADD COLUMN IF NOT EXISTS active BOOLEAN DEFAULT TRUE
                """)
                
                # Обновляем все существующие проекты, устанавливая active = TRUE
                cur.execute("""
                    UPDATE projects 
                    SET active = TRUE 
                    WHERE active IS NULL
                """)
                
                conn.commit()
                print("✅ Поле active успешно добавлено в таблицу projects")
                
    except Exception as e:
        print(f"❌ Ошибка при выполнении миграции: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if run_migration():
        print("🎉 Миграция выполнена успешно!")
    else:
        print("💥 Миграция не удалась!")
        sys.exit(1)