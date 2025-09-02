#!/usr/bin/env python3
"""
Миграция: Упрощение структуры таблицы навигации
Дата: 2025-01-19 12:00:00
Описание: Упрощаем структуру navigation_items до 7 основных полей
"""

import psycopg2
import os
from datetime import datetime

def up(cursor):
    """Выполняет миграцию упрощения структуры навигации"""
    
    print("🔄 Начинаем упрощение структуры таблицы навигации...")
    
    # 1. Создаем новую упрощенную таблицу
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS navigation_items_new (
            id SERIAL PRIMARY KEY,
            title VARCHAR(100) NOT NULL,                    -- Название пункта меню
            url VARCHAR(255) NOT NULL,                      -- Ссылка
            platform VARCHAR(20) NOT NULL DEFAULT 'webapp', -- Платформа: dashboard или webapp
            sort_order INTEGER DEFAULT 0,                  -- Порядок сортировки
            parent_id INTEGER DEFAULT NULL,                -- Родительский элемент (на будущее)
            is_active BOOLEAN DEFAULT TRUE,                 -- Активность (отображается или нет)
            
            -- Индексы
            FOREIGN KEY (parent_id) REFERENCES navigation_items_new(id) ON DELETE CASCADE
        );
    """)
    
    # 2. Создаем индексы для производительности
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_navigation_new_platform ON navigation_items_new(platform);
        CREATE INDEX IF NOT EXISTS idx_navigation_new_sort_order ON navigation_items_new(sort_order);
        CREATE INDEX IF NOT EXISTS idx_navigation_new_active ON navigation_items_new(is_active);
        CREATE INDEX IF NOT EXISTS idx_navigation_new_parent ON navigation_items_new(parent_id);
    """)
    
    # 3. Переносим данные из старой таблицы в новую с определением платформы
    cursor.execute("""
        INSERT INTO navigation_items_new (id, title, url, platform, sort_order, parent_id, is_active)
        SELECT 
            id,
            title,
            url,
            CASE 
                WHEN url LIKE '/dashboard/%' THEN 'dashboard'
                ELSE 'webapp'
            END as platform,
            sort_order,
            parent_id,
            is_active
        FROM navigation_items
        WHERE is_active = true
        ORDER BY sort_order;
    """)
    
    # 4. Получаем максимальный ID для корректировки последовательности
    cursor.execute("SELECT MAX(id) AS max_id FROM navigation_items_new;")
    row = cursor.fetchone()
    max_id = row['max_id'] if isinstance(row, dict) else (row[0] if row else None)
    if max_id:
        cursor.execute(f"SELECT setval('navigation_items_new_id_seq', {int(max_id)});")
    
    # 5. Переименовываем таблицы
    cursor.execute("DROP TABLE IF EXISTS navigation_items_old;")
    cursor.execute("ALTER TABLE navigation_items RENAME TO navigation_items_old;")
    cursor.execute("ALTER TABLE navigation_items_new RENAME TO navigation_items;")
    
    # 6. Переименовываем последовательность, если она существует
    cursor.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_class WHERE relkind = 'S' AND relname = 'navigation_items_new_id_seq'
            ) THEN
                ALTER SEQUENCE navigation_items_new_id_seq RENAME TO navigation_items_id_seq;
            END IF;
        END $$;
    """)
    
    # 7. Добавляем комментарии
    cursor.execute("""
        COMMENT ON TABLE navigation_items IS 'Упрощенная таблица навигации для dashboard и webapp';
        COMMENT ON COLUMN navigation_items.platform IS 'Платформа: dashboard или webapp';
        COMMENT ON COLUMN navigation_items.sort_order IS 'Порядок отображения (чем меньше, тем выше)';
        COMMENT ON COLUMN navigation_items.parent_id IS 'ID родительского элемента для иерархии';
        COMMENT ON COLUMN navigation_items.is_active IS 'Активность элемента (отображается или нет)';
    """)
    
    # 8. Показываем результат (RealDictCursor совместимость)
    cursor.execute("SELECT COUNT(*) AS cnt FROM navigation_items;")
    row = cursor.fetchone()
    total_count = row['cnt'] if isinstance(row, dict) else (row[0] if row else 0)
    
    cursor.execute("SELECT COUNT(*) AS cnt FROM navigation_items WHERE platform = 'dashboard';")
    row = cursor.fetchone()
    dashboard_count = row['cnt'] if isinstance(row, dict) else (row[0] if row else 0)
    
    cursor.execute("SELECT COUNT(*) AS cnt FROM navigation_items WHERE platform = 'webapp';")
    row = cursor.fetchone()
    webapp_count = row['cnt'] if isinstance(row, dict) else (row[0] if row else 0)
    
    print(f"✅ Миграция завершена успешно!")
    print(f"📊 Всего элементов навигации: {total_count}")
    print(f"🖥️  Dashboard элементов: {dashboard_count}")
    print(f"📱 WebApp элементов: {webapp_count}")
    
    return True

def down(cursor):
    """Откат миграции"""
    print("🔄 Откатываем миграцию упрощения навигации...")
    
    # Восстанавливаем старую таблицу
    cursor.execute("DROP TABLE IF EXISTS navigation_items;")
    cursor.execute("ALTER TABLE navigation_items_old RENAME TO navigation_items;")
    
    print("✅ Откат миграции завершен")
    return True

if __name__ == "__main__":
    # Подключение к базе данных
    try:
        # Локальная разработка (Docker)
        conn = psycopg2.connect(
            host="localhost",
            database="telegram_app", 
            user="postgres",
            password="postgres",
            port=5432
        )
        
        cursor = conn.cursor()
        
        # Выполняем миграцию
        if run_migration(cursor):
            conn.commit()
            print("🎉 Миграция применена успешно!")
        else:
            conn.rollback()
            print("❌ Ошибка при выполнении миграции")
            
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()