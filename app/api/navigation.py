"""
API для навигации
"""
from fastapi import APIRouter, HTTPException
from app.database.repositories.user_repository import user_repository

router = APIRouter()


@router.get("/navigation")
async def get_navigation(category: str = "main", user_id: int = None):
    """Получить навигационное меню"""
    try:
        # Базовая навигация для главной страницы
        if category == "main":
            navigation = [
                {
                    "id": "dashboard",
                    "title": "Главная",
                    "icon": "🏠",
                    "url": "/dashboard/main.html",
                    "active": True
                },
                {
                    "id": "tasks",
                    "title": "Задачи",
                    "icon": "✅",
                    "url": "/dashboard/tasks.html",
                    "active": False
                },
                {
                    "id": "events",
                    "title": "События",
                    "icon": "📅",
                    "url": "/dashboard/events.html",
                    "active": False
                },
                {
                    "id": "shopping",
                    "title": "Покупки",
                    "icon": "🛒",
                    "url": "/dashboard/shopping.html",
                    "active": False
                },
                {
                    "id": "projects",
                    "title": "Проекты",
                    "icon": "📁",
                    "url": "/dashboard/projects.html",
                    "active": False
                },
                {
                    "id": "notes",
                    "title": "Заметки",
                    "icon": "📝",
                    "url": "/dashboard/notes.html",
                    "active": False
                }
            ]
            
            # Если передан user_id, проверяем что пользователь существует
            if user_id:
                db_user_id = user_repository.resolve_user_id(user_id)
                if db_user_id:
                    # Добавляем базовые счетчики (пока 0)
                    for item in navigation:
                        if item["id"] in ["tasks", "events", "shopping"]:
                            item["count"] = 0
            
            return navigation
        
        # Другие категории навигации
        elif category == "settings":
            return [
                {
                    "id": "profile",
                    "title": "Профиль",
                    "icon": "👤",
                    "url": "/dashboard/profile.html"
                },
                {
                    "id": "notifications",
                    "title": "Уведомления",
                    "icon": "🔔",
                    "url": "/dashboard/notifications.html"
                },
                {
                    "id": "theme",
                    "title": "Тема",
                    "icon": "🎨",
                    "url": "/dashboard/theme.html"
                }
            ]
        
        else:
            return []
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching navigation: {str(e)}")


@router.get("/user/validate")
async def validate_user(user_id: int):
    """Проверить валидность пользователя"""
    try:
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Получаем базовую информацию о пользователе
        settings = user_repository.get_user_settings(db_user_id)
        
        return {
            "valid": True,
            "user_id": user_id,
            "db_id": db_user_id,
            "settings": settings,
            "status": "active"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating user: {str(e)}")


@router.get("/dashboard/stats")
async def get_dashboard_stats(user_id: int):
    """Получить статистику для дашборда"""
    try:
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Базовая статистика (пока без подсчета реальных данных)
        return {
            "tasks": {
                "total": 0,
                "active": 0,
                "completed": 0
            },
            "events": {
                "total": 0,
                "upcoming": 0
            },
            "shopping": {
                "total": 0,
                "pending": 0
            },
            "user": {
                "id": user_id,
                "db_id": db_user_id,
                "status": "active"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard stats: {str(e)}")