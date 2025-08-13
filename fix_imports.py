"""
Скрипт для исправления импортов в новой архитектуре
"""
import os
import sys

# Добавляем корневую директорию в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Тестирование всех импортов"""
    try:
        print("🔍 Проверка импортов...")
        
        # Проверяем основные модули
        from app.core.config import settings
        print("✅ app.core.config - OK")
        
        from app.database.connection import get_db_connection
        print("✅ app.database.connection - OK")
        
        from app.database.repositories.user_repository import user_repository
        print("✅ app.database.repositories.user_repository - OK")
        
        from app.database.repositories.shopping_repository import shopping_repository
        print("✅ app.database.repositories.shopping_repository - OK")
        
        from app.api.auth import router as auth_router
        print("✅ app.api.auth - OK")
        
        from app.api.shopping import router as shopping_router
        print("✅ app.api.shopping - OK")
        
        from app.telegram.bot import setup_telegram_app
        print("✅ app.telegram.bot - OK")
        
        from app.telegram.handlers import start
        print("✅ app.telegram.handlers - OK")
        
        # Проверяем основное приложение
        from app.main import create_app
        app = create_app()
        print("✅ app.main - OK")
        
        print("\n🎉 Все импорты работают корректно!")
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)