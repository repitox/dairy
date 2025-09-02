"""
Конфигурация тестов pytest
"""
import pytest
import asyncio
import os
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient

# Устанавливаем режим тестирования
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "postgresql://postgres:password@db:5432/telegram_app"

from app.main import create_app
from app.database.init import initialize_database


@pytest.fixture(scope="session")
def event_loop():
    """Создание event loop для всей сессии тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def app():
    """Создание тестового приложения"""
    test_app = create_app()
    
    # Инициализируем тестовую БД
    initialize_database()
    
    yield test_app


@pytest.fixture(scope="session")
async def client(app):
    """Создание асинхронного HTTP клиента для тестов"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as ac:
        yield ac


@pytest.fixture
def sync_client(app):
    """Создание синхронного HTTP клиента для простых тестов"""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def test_user_data():
    """Тестовые данные пользователя"""
    return {
        "telegram_id": 123456789,
        "first_name": "Test",
        "username": "testuser"
    }


@pytest.fixture
def test_shopping_item_data():
    """Тестовые данные для покупки"""
    return {
        "name": "Test Item",
        "quantity": 2,
        "price": 100.50,
        "category": "food",
        "user_id": 123456789
    }


@pytest.fixture
def test_event_data():
    """Тестовые данные для события"""
    return {
        "title": "Test Event",
        "location": "Test Location",
        "start_at": "2024-12-25T10:00:00",
        "end_at": "2024-12-25T12:00:00",
        "user_id": 123456789
    }


@pytest.fixture
def test_birthday_data():
    """Тестовые данные дня рождения"""
    return {
        "full_name": "Иван Петров",
        "day": 15,
        "month": 7,
        "year": 1990,
        "description": "Друг"
    }


@pytest.fixture
def test_task_data():
    """Тестовые данные для задачи"""
    return {
        "title": "Test Task",
        "description": "Test Description",
        "due_date": "2024-12-25",
        "priority": "высокая",
        "user_id": 123456789
    }
