#!/usr/bin/env python3
"""
Запуск сервера для тестирования
"""
import uvicorn
import os
import sys
import time

def init_database():
    """Инициализация базы данных при запуске"""
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            from app.database.init import initialize_database
            print("🗄️ Инициализация базы данных...")
            initialize_database()
            print("✅ База данных готова!")
            
            # Запускаем автоматическую миграцию если нужно
            run_auto_migration()
            return True
        except Exception as e:
            retry_count += 1
            if retry_count < max_retries:
                print(f"⏳ Ожидание БД... попытка {retry_count}/{max_retries}")
                print(f"   Ошибка: {e}")
                time.sleep(2)
            else:
                print(f"⚠️ Ошибка инициализации БД после {max_retries} попыток: {e}")
                print("🔄 Продолжаем запуск без БД...")
                return False

def run_auto_migration():
    """Автоматический запуск миграции при необходимости"""
    try:
        print("🔍 Проверка необходимости миграции...")
        
        # Импортируем функции миграции если они существуют
        try:
            from deploy_migrate import check_migration_needed, run_migration
            
            # Проверяем, нужна ли миграция
            status = check_migration_needed()
            
            if 'error' in status:
                print(f"⚠️ Ошибка проверки миграции: {status['error']}")
                return
            
            if not status.get('migration_needed', False):
                print("✅ Миграция не требуется")
                return
            
            print("🔄 Запуск автоматической миграции...")
            success = run_migration()
            
            if success:
                print("🎉 Автоматическая миграция завершена успешно!")
            else:
                print("⚠️ Миграция не удалась, но сервер продолжит работу")
        except ImportError:
            print("ℹ️ Система миграций недоступна (это нормально)")
            
    except Exception as e:
        print(f"⚠️ Ошибка автоматической миграции: {e}")
        print("🔄 Сервер продолжит работу")

if __name__ == "__main__":
    print("🚀 Запуск Telegram App...")
    print()
    
    # Инициализируем базу данных
    db_ok = init_database()
    
    print("🌐 Доступные URL:")
    print("🏠 Главная страница: http://localhost:8000/dashboard/")
    print("🔧 Локальная авторизация: http://localhost:8000/local-auth")
    print("📱 Тест Telegram авторизации: http://localhost:8000/test-auth")
    print("⚡ WebApp: http://localhost:8000/webapp/")
    
    # Показываем информацию о Docker, если запущен в контейнере
    if os.path.exists('/.dockerenv'):
        print("🐳 Запущено в Docker контейнере")
        print("🗄️ Adminer (БД): http://localhost:8080")
    
    print()
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0", 
        port=8000,
        reload=True
    )