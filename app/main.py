"""
Основное FastAPI приложение
"""
import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.api import auth, shopping, events, tasks, projects, notes, dashboard, navigation, tags
from app.api import birthdays
from app.telegram.bot import setup_telegram_app, start_reminder_loop


def create_app() -> FastAPI:
    """Создание FastAPI приложения"""
    app = FastAPI(title="Dialist API", version="1.0.0")
    
    # Подключаем статические файлы
    app.mount("/webapp", StaticFiles(directory="static", html=True), name="webapp")
    app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")
    
    # Подключаем API роутеры
    app.include_router(auth.router, prefix="/api", tags=["auth"])
    app.include_router(shopping.router, prefix="/api", tags=["shopping"])
    app.include_router(events.router, prefix="/api", tags=["events"])
    app.include_router(tasks.router, prefix="/api", tags=["tasks"])
    app.include_router(projects.router, prefix="/api", tags=["projects"])
    app.include_router(notes.router, prefix="/api", tags=["notes"])
    app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
    app.include_router(navigation.router, prefix="/api", tags=["navigation"])
    app.include_router(birthdays.router, prefix="/api", tags=["birthdays"])
    app.include_router(tags.router, prefix="/api", tags=["tags"])
    
    # Главная страница
    @app.get("/")
    async def root():
        """Главная страница проекта"""
        return FileResponse("index.html")
    
    @app.get("/test-auth")
    async def test_auth():
        return FileResponse("test_auth.html")
    
    @app.get("/local-auth")
    async def local_auth():
        return FileResponse("local_auth.html")
    
    return app


# Создаем приложение
app = create_app()

# Настраиваем Telegram бота
telegram_app = setup_telegram_app()

# Подключаем webhook для Telegram
from app.telegram.webhook import setup_webhook
setup_webhook(app, telegram_app)

# Запускаем цикл напоминаний при старте
@app.on_event("startup")
async def startup_event():
    """События при запуске приложения"""
    # Инициализация базы данных
    from app.database.init import initialize_database
    initialize_database()
    
    # Запуск цикла напоминаний
    asyncio.create_task(start_reminder_loop())
