"""
API для навигации
"""
from fastapi import APIRouter, HTTPException
from app.database.repositories.user_repository import user_repository

router = APIRouter()


@router.get("/navigation")
async def get_navigation(category: str = "main", user_id: int = None):
    """Получить навигационное меню из БД (упрощенная схема c platform)."""
    try:
        # Подключение к БД новой подсистемы
        from app.database.connection import get_db_cursor

        # Забираем только элементы dashboard
        with get_db_cursor() as cur:
            cur.execute(
                """
                SELECT id, title, url, platform, sort_order, parent_id, is_active
                FROM navigation_items
                WHERE platform = 'dashboard' AND is_active = TRUE
                ORDER BY sort_order ASC, title ASC
                """
            )
            rows = cur.fetchall()

        # Маппинг иконок (так как в новой схеме нет поля icon)
        def pick_icon(title: str) -> str:
            t = (title or '').lower()
            if 'главн' in t or 'home' in t: return '🏠'
            if 'задач' in t or 'task' in t: return '✅'
            if 'встреч' in t or 'событ' in t or 'event' in t: return '📅'
            if 'дн' in t and 'рожден' in t: return '🎂'
            if 'покуп' in t or 'shop' in t: return '🛒'
            if 'проект' in t or 'project' in t: return '📁'
            if 'замет' in t or 'note' in t: return '📝'
            if 'настрой' in t or 'settings' in t: return '⚙️'
            if 'ui' in t or 'kit' in t: return '🎨'
            return '•'

        # Преобразуем в формат, ожидаемый фронтом
        items = []
        by_parent = {}
        for r in rows:
            item = {
                "id": r["id"],
                "title": r["title"],
                "url": r["url"],
                "icon": pick_icon(r["title"]),
                "sort_order": r["sort_order"],
                "parent_id": r["parent_id"],
            }
            items.append(item)
            if r["parent_id"]:
                by_parent.setdefault(r["parent_id"], []).append(item)

        # Строим иерархию
        top_level = []
        for it in items:
            if it["parent_id"] is None:
                it["children"] = by_parent.get(it["id"], [])
                top_level.append(it)

        return top_level
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
