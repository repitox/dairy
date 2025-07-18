#!/usr/bin/env python3
"""
Скрипт для проверки статуса продакшена после исправлений
"""

import requests
import json
import psycopg2
from datetime import datetime

# Конфигурация для продакшена
PROD_API_URL = "https://rptx.na4u.ru"
DB_CONFIG = {
    "host": "postgres.c107597.h2",
    "database": "c107597_rptx_na4u_ru",
    "user": "c107597_rptx_na4u_ru",
    "password": "ZiKceXoydixol93"
}

def check_database_connection():
    """Проверка подключения к базе данных"""
    print("🔍 Проверка подключения к базе данных...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Проверяем существование таблиц
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename;
        """)
        
        tables = cursor.fetchall()
        print(f"   ✅ Подключение к БД установлено")
        print(f"   📊 Найдено таблиц: {len(tables)}")
        
        expected_tables = ['users', 'projects', 'tasks', 'events', 'purchases', 'notes', 'settings']
        existing_tables = [table[0] for table in tables]
        
        for table in expected_tables:
            if table in existing_tables:
                print(f"   ✅ Таблица '{table}' существует")
            else:
                print(f"   ❌ Таблица '{table}' отсутствует")
        
        # Проверяем количество записей
        for table in expected_tables:
            if table in existing_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = cursor.fetchone()[0]
                print(f"   📊 {table}: {count} записей")
        
        # Проверяем структуру таблицы purchases
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'purchases' 
            ORDER BY ordinal_position;
        """)
        
        purchases_columns = cursor.fetchall()
        print(f"   📊 Колонки в таблице purchases:")
        for col in purchases_columns:
            print(f"      - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка подключения к БД: {e}")
        return False

def check_api_endpoints():
    """Проверка API endpoints"""
    print("\n🔍 Проверка API endpoints...")
    
    test_user_id = 1
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    endpoints_to_check = [
        ("GET", "/api/projects", {"user_id": test_user_id}, "Проекты"),
        ("GET", "/api/tasks", {"user_id": test_user_id}, "Задачи"),
        ("GET", "/api/tasks/today", {"user_id": test_user_id}, "Задачи на сегодня"),
        ("GET", "/api/events", {"user_id": test_user_id}, "События"),
        ("GET", "/api/shopping", {"user_id": test_user_id}, "Покупки"),
        ("GET", "/api/notes", {"user_id": test_user_id}, "Заметки"),
        ("GET", "/api/settings", {"user_id": test_user_id}, "Настройки"),
    ]
    
    success_count = 0
    total_count = len(endpoints_to_check)
    
    for method, endpoint, params, description in endpoints_to_check:
        try:
            url = f"{PROD_API_URL}{endpoint}"
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ {description}: {response.status_code}")
                success_count += 1
                
                # Показываем количество записей если это массив
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"      📊 Получено {len(data)} записей")
                    elif isinstance(data, dict) and "id" in data:
                        print(f"      🆔 ID: {data['id']}")
                except:
                    pass
                    
            else:
                print(f"   ❌ {description}: {response.status_code}")
                if response.text:
                    print(f"      Error: {response.text[:100]}...")
                    
        except Exception as e:
            print(f"   ❌ {description}: {str(e)}")
    
    print(f"\n   📊 Результат: {success_count}/{total_count} endpoints работают")
    return success_count / total_count

def test_crud_operations():
    """Тестирование CRUD операций"""
    print("\n🔍 Тестирование CRUD операций...")
    
    test_user_id = 1
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Тестируем создание заметки
    print("   📝 Тестирование создания заметки...")
    note_data = {
        "title": f"Тестовая заметка {datetime.now().strftime('%H:%M:%S')}",
        "content": "Автоматически созданная заметка для тестирования",
        "user_id": test_user_id
    }
    
    try:
        response = requests.post(
            f"{PROD_API_URL}/api/notes",
            json=note_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print(f"   ✅ Заметка создана: {response.status_code}")
            note_id = response.json().get("id")
            print(f"      🆔 ID: {note_id}")
            
            # Тестируем получение заметки
            if note_id:
                get_response = requests.get(
                    f"{PROD_API_URL}/api/notes/{note_id}",
                    params={"user_id": test_user_id},
                    headers=headers,
                    timeout=10
                )
                
                if get_response.status_code == 200:
                    print(f"   ✅ Заметка получена: {get_response.status_code}")
                else:
                    print(f"   ❌ Ошибка получения заметки: {get_response.status_code}")
            
        else:
            print(f"   ❌ Ошибка создания заметки: {response.status_code}")
            print(f"      Error: {response.text[:100]}...")
            
    except Exception as e:
        print(f"   ❌ Ошибка при тестировании заметки: {e}")
    
    # Тестируем создание покупки
    print("   🛒 Тестирование создания покупки...")
    shopping_data = {
        "name": f"Тестовая покупка {datetime.now().strftime('%H:%M:%S')}",
        "quantity": 1,
        "price": 99.99,
        "user_id": test_user_id
    }
    
    try:
        response = requests.post(
            f"{PROD_API_URL}/api/shopping",
            json=shopping_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print(f"   ✅ Покупка создана: {response.status_code}")
            shopping_id = response.json().get("id")
            print(f"      🆔 ID: {shopping_id}")
        else:
            print(f"   ❌ Ошибка создания покупки: {response.status_code}")
            print(f"      Error: {response.text[:100]}...")
            
    except Exception as e:
        print(f"   ❌ Ошибка при тестировании покупки: {e}")

def check_documentation():
    """Проверка документации API"""
    print("\n🔍 Проверка документации API...")
    
    docs_endpoints = [
        "/docs",
        "/redoc",
        "/openapi.json"
    ]
    
    for endpoint in docs_endpoints:
        try:
            response = requests.get(f"{PROD_API_URL}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"   ✅ {endpoint}: доступен")
            else:
                print(f"   ❌ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint}: {str(e)}")

def main():
    print("🚀 Проверка статуса продакшена после исправлений")
    print("=" * 70)
    
    # Проверка базы данных
    db_ok = check_database_connection()
    
    # Проверка API
    api_success_rate = check_api_endpoints()
    
    # Тестирование CRUD
    test_crud_operations()
    
    # Проверка документации
    check_documentation()
    
    # Общий результат
    print("\n" + "=" * 70)
    print("📊 ОБЩИЙ РЕЗУЛЬТАТ:")
    
    if db_ok:
        print("   ✅ База данных: в порядке")
    else:
        print("   ❌ База данных: есть проблемы")
    
    if api_success_rate > 0.8:
        print(f"   ✅ API: в порядке ({api_success_rate:.1%} endpoints работают)")
    elif api_success_rate > 0.5:
        print(f"   ⚠️  API: частично работает ({api_success_rate:.1%} endpoints работают)")
    else:
        print(f"   ❌ API: есть проблемы ({api_success_rate:.1%} endpoints работают)")
    
    # Рекомендации
    print("\n💡 РЕКОМЕНДАЦИИ:")
    
    if not db_ok:
        print("1. Выполните скрипт fix_production_db.sql")
        print("2. Проверьте права доступа к базе данных")
        print("3. Убедитесь что все миграции выполнены")
    
    if api_success_rate < 0.8:
        print("1. Перезапустите приложение")
        print("2. Проверьте логи сервера")
        print("3. Убедитесь что код синхронизирован")
    
    print("\n🔧 КОМАНДЫ ДЛЯ ИСПРАВЛЕНИЯ:")
    print("# Подключение к серверу:")
    print("ssh c107597@h60.netangels.ru")
    print()
    print("# Исправление БД:")
    print("psql -h postgres.c107597.h2 -U c107597_rptx_na4u_ru -d c107597_rptx_na4u_ru -f fix_production_db.sql")
    print()
    print("# Повторная проверка:")
    print("python check_production_status.py")

if __name__ == "__main__":
    main()