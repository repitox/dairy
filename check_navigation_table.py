#!/usr/bin/env python3
"""
Скрипт для проверки и создания таблицы navigation_items
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import get_conn

def check_and_create_navigation_table():
    """Проверяет существование таблицы navigation_items и создает её при необходимости"""
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Проверяем существование таблицы
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'navigation_items'
                    );
                """)
                
                table_exists = cur.fetchone()[0]
                
                if table_exists:
                    print("✅ Таблица navigation_items уже существует")
                    
                    # Проверяем количество записей
                    cur.execute("SELECT COUNT(*) FROM navigation_items")
                    count = cur.fetchone()[0]
                    print(f"📊 Количество записей в navigation_items: {count}")
                    
                    if count > 0:
                        cur.execute("SELECT title, url, sort_order FROM navigation_items ORDER BY sort_order")
                        items = cur.fetchall()
                        print("\n📋 Существующие пункты навигации:")
                        for item in items:
                            print(f"  - {item['title']} ({item['url']}) [order: {item['sort_order']}]")
                    
                else:
                    print("❌ Таблица navigation_items не существует. Создаём...")
                    
                    # Создаём таблицу
                    cur.execute("""
                        CREATE TABLE navigation_items (
                            id SERIAL PRIMARY KEY,
                            title VARCHAR(100) NOT NULL,
                            url VARCHAR(255) NOT NULL,
                            icon VARCHAR(50),
                            description TEXT,
                            sort_order INTEGER DEFAULT 0,
                            is_active BOOLEAN DEFAULT TRUE,
                            is_visible BOOLEAN DEFAULT TRUE,
                            category VARCHAR(50) DEFAULT 'main',
                            group_name VARCHAR(50),
                            parent_id INTEGER REFERENCES navigation_items(id),
                            badge_text VARCHAR(20),
                            badge_color VARCHAR(20),
                            css_classes TEXT,
                            attributes JSONB DEFAULT '{}',
                            required_role VARCHAR(50),
                            required_permission VARCHAR(100),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            created_by INTEGER,
                            updated_by INTEGER
                        );
                    """)
                    
                    print("✅ Таблица navigation_items создана")
                    
                    # Добавляем базовые пункты навигации
                    navigation_items = [
                        ('Главная', 'main.html', '🏠', 'Главная страница dashboard', 10),
                        ('Задачи', 'tasks.html', '✅', 'Управление задачами', 20),
                        ('Встречи', 'meetings.html', '📅', 'Планирование встреч', 30),
                        ('Проекты', 'projects.html', '📁', 'Управление проектами', 40),
                        ('Покупки', 'shopping.html', '🛒', 'Списки покупок', 50),
                        ('Заметки', 'notes.html', '📝', 'Личные заметки', 60),
                        ('Настройки', 'settings.html', '⚙️', 'Настройки пользователя', 70)
                    ]
                    
                    for title, url, icon, description, sort_order in navigation_items:
                        cur.execute("""
                            INSERT INTO navigation_items (title, url, icon, description, sort_order, category)
                            VALUES (%s, %s, %s, %s, %s, 'main')
                        """, (title, url, icon, description, sort_order))
                    
                    print(f"✅ Добавлено {len(navigation_items)} базовых пунктов навигации")
                    
                conn.commit()
                
    except Exception as e:
        print(f"❌ Ошибка при работе с таблицей navigation_items: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔍 Проверка таблицы navigation_items...")
    success = check_and_create_navigation_table()
    
    if success:
        print("\n✅ Проверка завершена успешно")
    else:
        print("\n❌ Проверка завершена с ошибками")
        sys.exit(1)