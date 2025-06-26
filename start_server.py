#!/usr/bin/env python3
"""
Запуск сервера для тестирования
"""
import uvicorn

if __name__ == "__main__":
    print("🚀 Запуск сервера...")
    print("📱 Тест авторизации: http://localhost:8000/test-auth")
    print("🏠 Главная страница: http://localhost:8000/dashboard/")
    print("⚡ WebApp: http://localhost:8000/webapp/")
    print()
    
    uvicorn.run(
        "bot:app",  # Передаем как строку импорта
        host="0.0.0.0", 
        port=8000,
        reload=True
    )