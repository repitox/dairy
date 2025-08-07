#!/usr/bin/env python3
"""
Скрипт для управления навигацией
Позволяет добавлять, редактировать и удалять пункты навигации
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import get_conn
import json

def show_navigation():
    """Показать все пункты навигации"""
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        id, title, url, icon, description, 
                        sort_order, category, is_active, is_visible,
                        CASE 
                            WHEN url LIKE '/dashboard/%' THEN '🖥️ Dashboard'
                            ELSE '📱 WebApp'
                        END as type
                    FROM navigation_items 
                    ORDER BY category, sort_order
                """)
                items = cur.fetchall()
                
                if not items:
                    print("❌ Пункты навигации не найдены")
                    return
                
                print(f"\n📋 Найдено {len(items)} пунктов навигации:\n")
                
                current_category = None
                for item in items:
                    if item['category'] != current_category:
                        current_category = item['category']
                        print(f"\n📂 Категория: {current_category.upper()}")
                        print("-" * 50)
                    
                    status = "✅" if item['is_active'] and item['is_visible'] else "❌"
                    print(f"{status} [{item['id']:2d}] {item['type']} {item['icon']} {item['title']}")
                    print(f"    URL: {item['url']}")
                    print(f"    Порядок: {item['sort_order']}")
                    if item['description']:
                        print(f"    Описание: {item['description']}")
                    print()
                    
    except Exception as e:
        print(f"❌ Ошибка при получении навигации: {e}")

def add_navigation_item():
    """Добавить новый пункт навигации"""
    print("\n➕ Добавление нового пункта навигации")
    print("-" * 40)
    
    try:
        title = input("Название пункта: ").strip()
        if not title:
            print("❌ Название не может быть пустым")
            return
        
        url = input("URL (например: tasks.html или /dashboard/reports.html): ").strip()
        if not url:
            print("❌ URL не может быть пустым")
            return
        
        icon = input("Иконка (emoji, например: 📋): ").strip() or "📄"
        description = input("Описание (опционально): ").strip() or None
        
        print("\nДоступные категории:")
        print("1. main - основные страницы")
        print("2. projects - управление проектами") 
        print("3. create - создание контента")
        print("4. settings - настройки")
        print("5. tools - инструменты")
        print("6. admin - администрирование")
        
        category_choice = input("Выберите категорию (1-6) или введите свою: ").strip()
        
        category_map = {
            '1': 'main',
            '2': 'projects', 
            '3': 'create',
            '4': 'settings',
            '5': 'tools',
            '6': 'admin'
        }
        
        category = category_map.get(category_choice, category_choice if category_choice else 'main')
        
        sort_order = input("Порядок сортировки (число, например: 15): ").strip()
        try:
            sort_order = int(sort_order) if sort_order else 50
        except ValueError:
            sort_order = 50
        
        # Определяем тип на основе URL
        nav_type = "🖥️ Dashboard" if url.startswith('/dashboard/') else "📱 WebApp"
        
        print(f"\n📋 Предварительный просмотр:")
        print(f"Тип: {nav_type}")
        print(f"Название: {title}")
        print(f"URL: {url}")
        print(f"Иконка: {icon}")
        print(f"Описание: {description or 'Не указано'}")
        print(f"Категория: {category}")
        print(f"Порядок: {sort_order}")
        
        confirm = input("\nСохранить пункт навигации? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ Отменено")
            return
        
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO navigation_items 
                    (title, url, icon, description, sort_order, category, is_active, is_visible)
                    VALUES (%s, %s, %s, %s, %s, %s, TRUE, TRUE)
                    RETURNING id
                """, (title, url, icon, description, sort_order, category))
                
                new_id = cur.fetchone()['id']
                conn.commit()
                
                print(f"✅ Пункт навигации добавлен с ID: {new_id}")
                
    except Exception as e:
        print(f"❌ Ошибка при добавлении пункта навигации: {e}")

def toggle_navigation_item():
    """Включить/выключить пункт навигации"""
    print("\n🔄 Включение/выключение пункта навигации")
    print("-" * 40)
    
    try:
        item_id = input("ID пункта навигации: ").strip()
        if not item_id.isdigit():
            print("❌ ID должен быть числом")
            return
        
        item_id = int(item_id)
        
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Проверяем существование пункта
                cur.execute("SELECT title, is_active FROM navigation_items WHERE id = %s", (item_id,))
                item = cur.fetchone()
                
                if not item:
                    print(f"❌ Пункт навигации с ID {item_id} не найден")
                    return
                
                new_status = not item['is_active']
                status_text = "включен" if new_status else "выключен"
                
                cur.execute("""
                    UPDATE navigation_items 
                    SET is_active = %s, updated_at = NOW()
                    WHERE id = %s
                """, (new_status, item_id))
                
                conn.commit()
                
                print(f"✅ Пункт '{item['title']}' {status_text}")
                
    except Exception as e:
        print(f"❌ Ошибка при изменении статуса пункта навигации: {e}")

def delete_navigation_item():
    """Удалить пункт навигации"""
    print("\n🗑️ Удаление пункта навигации")
    print("-" * 40)
    
    try:
        item_id = input("ID пункта навигации для удаления: ").strip()
        if not item_id.isdigit():
            print("❌ ID должен быть числом")
            return
        
        item_id = int(item_id)
        
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Проверяем существование пункта
                cur.execute("SELECT title FROM navigation_items WHERE id = %s", (item_id,))
                item = cur.fetchone()
                
                if not item:
                    print(f"❌ Пункт навигации с ID {item_id} не найден")
                    return
                
                print(f"⚠️ Вы собираетесь удалить пункт: '{item['title']}'")
                confirm = input("Подтвердите удаление (введите 'DELETE'): ").strip()
                
                if confirm != 'DELETE':
                    print("❌ Удаление отменено")
                    return
                
                cur.execute("DELETE FROM navigation_items WHERE id = %s", (item_id,))
                conn.commit()
                
                print(f"✅ Пункт навигации '{item['title']}' удален")
                
    except Exception as e:
        print(f"❌ Ошибка при удалении пункта навигации: {e}")

def show_navigation_by_type():
    """Показать навигацию по типам (WebApp/Dashboard)"""
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                print("\n📱 WebApp навигация (Telegram):")
                print("-" * 40)
                
                cur.execute("""
                    SELECT title, url, icon, category, sort_order
                    FROM navigation_items 
                    WHERE url NOT LIKE '/dashboard/%' 
                    AND url NOT LIKE '%dashboard%'
                    AND is_active = TRUE
                    ORDER BY category, sort_order
                """)
                webapp_items = cur.fetchall()
                
                if webapp_items:
                    current_category = None
                    for item in webapp_items:
                        if item['category'] != current_category:
                            current_category = item['category']
                            print(f"\n📂 {current_category.upper()}:")
                        print(f"  {item['icon']} {item['title']} → {item['url']}")
                else:
                    print("  Нет активных пунктов")
                
                print("\n🖥️ Dashboard навигация (Браузер):")
                print("-" * 40)
                
                cur.execute("""
                    SELECT title, url, icon, category, sort_order
                    FROM navigation_items 
                    WHERE is_active = TRUE
                    ORDER BY category, sort_order
                """)
                dashboard_items = cur.fetchall()
                
                if dashboard_items:
                    current_category = None
                    for item in dashboard_items:
                        if item['category'] != current_category:
                            current_category = item['category']
                            print(f"\n📂 {current_category.upper()}:")
                        
                        nav_type = "🖥️" if item['url'].startswith('/dashboard/') else "📱"
                        print(f"  {nav_type} {item['icon']} {item['title']} → {item['url']}")
                else:
                    print("  Нет активных пунктов")
                    
    except Exception as e:
        print(f"❌ Ошибка при получении навигации по типам: {e}")

def main():
    """Главное меню"""
    while True:
        print("\n" + "="*50)
        print("🧭 УПРАВЛЕНИЕ НАВИГАЦИЕЙ")
        print("="*50)
        print("1. 📋 Показать все пункты навигации")
        print("2. 📱🖥️ Показать навигацию по типам (WebApp/Dashboard)")
        print("3. ➕ Добавить новый пункт")
        print("4. 🔄 Включить/выключить пункт")
        print("5. 🗑️ Удалить пункт")
        print("6. 🚪 Выход")
        print("-" * 50)
        
        choice = input("Выберите действие (1-6): ").strip()
        
        if choice == '1':
            show_navigation()
        elif choice == '2':
            show_navigation_by_type()
        elif choice == '3':
            add_navigation_item()
        elif choice == '4':
            toggle_navigation_item()
        elif choice == '5':
            delete_navigation_item()
        elif choice == '6':
            print("👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    print("🧭 Скрипт управления навигацией")
    print("Убедитесь, что база данных доступна")
    
    try:
        # Проверяем подключение к БД
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM navigation_items")
                count = cur.fetchone()[0]
                print(f"✅ Подключение к БД успешно. Найдено {count} пунктов навигации.")
        
        main()
        
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        print("Убедитесь, что Docker контейнеры запущены: docker-compose up -d")
        sys.exit(1)