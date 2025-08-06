#!/usr/bin/env python3
"""
Скрипт для настройки навигации WebApp в БД
Добавляет пункты навигации для категории 'webapp'
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import get_conn

def setup_webapp_navigation():
    """Настройка навигации для WebApp"""
    
    # Пункты навигации для WebApp
    navigation_items = [
        # Основное
        {
            'id': 'webapp_home',
            'title': 'Главная',
            'url': 'index.html',
            'icon': '🏠',
            'description': 'Главная страница WebApp',
            'category': 'main',
            'sort_order': 1,
            'is_active': True,
            'is_visible': True
        },
        {
            'id': 'webapp_tasks',
            'title': 'Задачи',
            'url': 'tasks.html',
            'icon': '📋',
            'description': 'Управление задачами',
            'category': 'main',
            'sort_order': 2,
            'is_active': True,
            'is_visible': True
        },
        {
            'id': 'webapp_events',
            'title': 'События',
            'url': 'events.html',
            'icon': '📅',
            'description': 'Календарь событий',
            'category': 'main',
            'sort_order': 3,
            'is_active': True,
            'is_visible': True
        },
        {
            'id': 'webapp_shopping',
            'title': 'Покупки',
            'url': 'shopping.html',
            'icon': '🛒',
            'description': 'Список покупок',
            'category': 'main',
            'sort_order': 4,
            'is_active': True,
            'is_visible': True
        },
        
        # Проекты
        {
            'id': 'webapp_projects',
            'title': 'Все проекты',
            'url': 'project_select.html',
            'icon': '📁',
            'description': 'Просмотр всех проектов',
            'category': 'projects',
            'sort_order': 5,
            'is_active': True,
            'is_visible': True
        },
        {
            'id': 'webapp_project_create',
            'title': 'Создать проект',
            'url': 'project_create.html',
            'icon': '➕',
            'description': 'Создание нового проекта',
            'category': 'projects',
            'sort_order': 6,
            'is_active': True,
            'is_visible': True
        },
        
        # Создание
        {
            'id': 'webapp_task_add',
            'title': 'Новая задача',
            'url': 'task_add.html',
            'icon': '📝',
            'description': 'Создание новой задачи',
            'category': 'create',
            'sort_order': 7,
            'is_active': True,
            'is_visible': True
        },
        {
            'id': 'webapp_event_create',
            'title': 'Новое событие',
            'url': 'event_create.html',
            'icon': '📅',
            'description': 'Создание нового события',
            'category': 'create',
            'sort_order': 8,
            'is_active': True,
            'is_visible': True
        },
        {
            'id': 'webapp_shopping_add',
            'title': 'Добавить покупку',
            'url': 'shopping.html',
            'icon': '🛒',
            'description': 'Добавление новой покупки',
            'category': 'create',
            'sort_order': 9,
            'is_active': True,
            'is_visible': True
        },
        
        # Настройки
        {
            'id': 'webapp_settings',
            'title': 'Настройки',
            'url': 'settings.html',
            'icon': '⚙️',
            'description': 'Настройки приложения',
            'category': 'settings',
            'sort_order': 10,
            'is_active': True,
            'is_visible': True
        },
        {
            'id': 'webapp_timezone',
            'title': 'Часовой пояс',
            'url': 'timezone-settings.html',
            'icon': '🌍',
            'description': 'Настройка часового пояса',
            'category': 'settings',
            'sort_order': 11,
            'is_active': True,
            'is_visible': True
        }
    ]
    
    try:
        conn = get_conn()
        cursor = conn.cursor()
        
        print("🚀 Настройка навигации WebApp...")
        
        # Удаляем существующие записи WebApp навигации
        cursor.execute("""
            DELETE FROM navigation_items 
            WHERE title IN ('Главная', 'Задачи', 'События', 'Покупки', 'Все проекты', 'Создать проект', 
                           'Новая задача', 'Новое событие', 'Добавить покупку', 'Настройки', 'Часовой пояс')
            AND category IN ('main', 'projects', 'create', 'settings')
        """)
        
        deleted_count = cursor.rowcount
        print(f"🗑️ Удалено {deleted_count} старых записей WebApp навигации")
        
        # Добавляем новые записи
        insert_query = """
            INSERT INTO navigation_items (
                title, url, icon, description, sort_order,
                badge_text, badge_color, css_classes, attributes,
                category, group_name, parent_id, is_active, is_visible,
                required_role, required_permission, created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, NOW(), NOW()
            )
        """
        
        added_count = 0
        for item in navigation_items:
            cursor.execute(insert_query, (
                item['title'],
                item['url'],
                item['icon'],
                item['description'],
                item['sort_order'],
                item.get('badge_text'),
                item.get('badge_color'),
                item.get('css_classes'),
                item.get('attributes'),
                item['category'],
                item.get('group_name'),
                item.get('parent_id'),
                item['is_active'],
                item['is_visible'],
                item.get('required_role'),
                item.get('required_permission')
            ))
            added_count += 1
            print(f"✅ Добавлен: {item['title']} ({item['category']})")
        
        conn.commit()
        
        print(f"\n🎉 Навигация WebApp настроена успешно!")
        print(f"📊 Добавлено {added_count} пунктов навигации")
        print(f"📱 Категории: main, projects, create, settings")
        
        # Проверяем результат
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM navigation_items 
            WHERE category IN ('main', 'projects', 'create', 'settings') AND is_active = TRUE
            GROUP BY category
            ORDER BY category
        """)
        
        categories = cursor.fetchall()
        print(f"\n📋 Статистика по категориям:")
        for category, count in categories:
            print(f"   {category}: {count} пунктов")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка настройки навигации: {e}")
        return False

def test_navigation_api():
    """Тестирование API навигации"""
    import requests
    
    try:
        print("\n🧪 Тестирование API навигации...")
        
        # Тестируем получение навигации для WebApp
        response = requests.get('http://localhost:8000/api/navigation?category=main')
        
        if response.status_code == 200:
            data = response.json()
            navigation_items = data.get('navigation', [])
            
            print(f"✅ API работает! Получено {len(navigation_items)} пунктов навигации")
            
            # Показываем первые несколько пунктов
            for item in navigation_items[:3]:
                print(f"   📄 {item['title']} - {item['url']} ({item['category']})")
            
            if len(navigation_items) > 3:
                print(f"   ... и еще {len(navigation_items) - 3} пунктов")
                
        else:
            print(f"❌ API вернул ошибку: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️ Сервер не запущен. Запустите bot.py для тестирования API")
    except Exception as e:
        print(f"❌ Ошибка тестирования API: {e}")

if __name__ == "__main__":
    print("🔧 Настройка навигации WebApp")
    print("=" * 50)
    
    success = setup_webapp_navigation()
    
    if success:
        test_navigation_api()
        
        print("\n" + "=" * 50)
        print("✅ Настройка завершена!")
        print("\n📝 Что дальше:")
        print("1. Запустите сервер: python bot.py")
        print("2. Откройте WebApp в Telegram")
        print("3. Проверьте работу навигации")
        print("4. Кнопка 'Назад' появится на всех страницах кроме главной")
    else:
        print("\n❌ Настройка не удалась!")
        sys.exit(1)