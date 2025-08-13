#!/usr/bin/env python3
"""
Демонстрация работы нового API
"""
import requests
import json

BASE_URL = "http://localhost:8001"

def test_api():
    """Тестирование API endpoints"""
    print("🚀 Демонстрация нового API")
    print("=" * 50)
    
    # Тест 1: Проверка несуществующего пользователя
    print("\n1. Тест получения несуществующего пользователя:")
    response = requests.get(f"{BASE_URL}/api/user-profile?user_id=999999")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Тест 2: Создание пользователя через репозиторий (симуляция)
    print("\n2. Тест создания пользователя:")
    print("   (Пользователь будет создан автоматически при первом обращении)")
    
    # Тест 3: Обновление настроек пользователя
    print("\n3. Тест обновления настроек пользователя:")
    test_user_id = 123456789
    settings_data = {
        "user_id": test_user_id,
        "key": "theme",
        "value": "dark"
    }
    response = requests.post(f"{BASE_URL}/api/user-settings", json=settings_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Тест 4: Получение настроек пользователя
    print("\n4. Тест получения настроек пользователя:")
    response = requests.get(f"{BASE_URL}/api/user-settings?user_id={test_user_id}")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Тест 5: Добавление товара в список покупок
    print("\n5. Тест добавления товара в список покупок:")
    shopping_data = {
        "name": "Тестовый товар",
        "quantity": 2,
        "price": 100.50,
        "category": "food",
        "user_id": test_user_id
    }
    response = requests.post(f"{BASE_URL}/api/shopping", json=shopping_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Тест 6: Получение списка покупок
    print("\n6. Тест получения списка покупок:")
    response = requests.get(f"{BASE_URL}/api/shopping?user_id={test_user_id}")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        items = response.json()
        print(f"   Найдено товаров: {len(items)}")
        if items:
            print(f"   Первый товар: {items[0]['name']}")
    else:
        print(f"   Response: {response.json()}")
    
    print("\n" + "=" * 50)
    print("✅ Демонстрация завершена!")
    print(f"🌐 Приложение доступно по адресу: {BASE_URL}")
    print("📚 Документация API: {}/docs".format(BASE_URL))

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка подключения!")
        print("Убедитесь, что приложение запущено:")
        print("   docker-compose -f docker-compose.new.yml up -d app-new db")
    except Exception as e:
        print(f"❌ Ошибка: {e}")