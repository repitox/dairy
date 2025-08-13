#!/usr/bin/env python3
"""
Совместимость со старой структурой для NetAngels
Этот файл заменяет старый bot.py и запускает новое приложение
"""
import os
import sys

# Добавляем родительскую директорию в PYTHONPATH
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Устанавливаем переменные окружения для продакшена
os.environ.setdefault("ENVIRONMENT", "production")
os.environ.setdefault("VERIFY_TELEGRAM_SIGNATURE", "true")

# Импортируем и запускаем приложение
from app.main import app

# Для совместимости с uvicorn/gunicorn
application = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0", 
        port=int(os.environ.get("PORT", 8000)),
        log_level="info"
    )