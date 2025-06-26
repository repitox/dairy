#!/usr/bin/env python3
"""
Запуск сервера для тестирования
"""
import uvicorn
import os

def init_database():
    """Инициализация базы данных при запуске"""
    import time
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            from db import init_db
            print("🗄️ Инициализация базы данных...")
            init_db()
            print("✅ База данных готова!")
            return
        except Exception as e:
            retry_count += 1
            if retry_count < max_retries:
                print(f"⏳ Ожидание БД... попытка {retry_count}/{max_retries}")
                time.sleep(2)
            else:
                print(f"⚠️ Ошибка инициализации БД после {max_retries} попыток: {e}")
                print("🔄 Продолжаем запуск без БД...")
                break

if __name__ == "__main__":
    print("🚀 Запуск Telegram App...")
    print()
    
    # Инициализируем базу данных
    init_database()
    
    print("🌐 Доступные URL:")
    print("🔧 Локальная авторизация: http://localhost:8000/local-auth")
    print("🏠 Главная страница: http://localhost:8000/dashboard/")
    print("📱 Тест Telegram авторизации: http://localhost:8000/test-auth")
    print("⚡ WebApp: http://localhost:8000/webapp/")
    
    # Показываем информацию о Docker, если запущен в контейнере
    if os.path.exists('/.dockerenv'):
        print("🐳 Запущено в Docker контейнере")
        print("🗄️ Adminer (БД): http://localhost:8080")
    
    print()
    
    uvicorn.run(
        "bot:app",  # Передаем как строку импорта
        host="0.0.0.0", 
        port=8000,
        reload=True
    )