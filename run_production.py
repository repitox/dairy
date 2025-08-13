#!/usr/bin/env python3
"""
Точка входа для запуска приложения на хостинге NetAngels
"""
import os
import sys
import uvicorn

# Добавляем корневую директорию в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Устанавливаем переменные окружения для продакшена
os.environ.setdefault("ENVIRONMENT", "production")
os.environ.setdefault("VERIFY_TELEGRAM_SIGNATURE", "true")

# Импортируем приложение
from app.main import app

if __name__ == "__main__":
    # Запускаем приложение
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        log_level="info"
    )