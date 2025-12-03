"""
API для авторизации
"""
from fastapi import APIRouter, Request, HTTPException
from app.database.repositories.user_repository import user_repository
from app.core.config import settings

router = APIRouter()


@router.get("/user-profile")
async def get_user_profile(user_id: int):
    """Получить профиль пользователя"""
    try:
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        settings = user_repository.get_user_settings(db_user_id)
        return {
            "user_id": db_user_id,
            "settings": settings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user profile: {str(e)}")


@router.post("/user-settings")
async def update_user_settings(request: Request):
    """Обновить настройки пользователя"""
    data = await request.json()
    user_id = data.get("user_id")
    key = data.get("key")
    value = data.get("value")
    
    if not user_id or not key:
        raise HTTPException(status_code=400, detail="user_id and key required")
    
    try:
        user_repository.update_user_setting(user_id, key, value)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user setting: {str(e)}")


@router.get("/user-settings")
async def get_user_settings(user_id: int):
    """Получить настройки пользователя"""
    try:
        print(f"📖 GET /api/user-settings - user_id={user_id}")
        settings = user_repository.get_user_settings(user_id)
        print(f"✅ Настройки загружены: {settings}")
        return settings
    except Exception as e:
        print(f"❌ Ошибка в GET /api/user-settings: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching user settings: {str(e)}")


@router.get("/user-timezone")
async def get_user_timezone(user_id: int):
    """Получить часовой пояс пользователя"""
    try:
        timezone = user_repository.get_user_setting(user_id, "timezone") or "0"
        return {"timezone": timezone}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user timezone: {str(e)}")


@router.post("/user-timezone")
async def update_user_timezone(request: Request):
    """Обновить часовой пояс пользователя"""
    data = await request.json()
    user_id = data.get("user_id")
    timezone = data.get("timezone", "0")
    
    print(f"📝 POST /api/user-timezone - user_id={user_id}, timezone={timezone}")
    
    if not user_id:
        print(f"⚠️ user_id не предоставлен")
        raise HTTPException(status_code=400, detail="user_id required")
    
    try:
        user_repository.update_user_setting(user_id, "timezone", str(timezone))
        print(f"✅ Часовой пояс обновлен: user_id={user_id}, timezone={timezone}")
        return {"status": "ok"}
    except Exception as e:
        print(f"❌ Ошибка в POST /api/user-timezone: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating user timezone: {str(e)}")


@router.post("/auth/telegram")
async def telegram_auth(request: Request):
    """Авторизация через Telegram"""
    data = await request.json()
    
    # Извлекаем данные пользователя
    user_id = data.get("id")
    first_name = data.get("first_name", "")
    last_name = data.get("last_name", "")
    username = data.get("username", "")
    photo_url = data.get("photo_url", "")
    
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID required")
    
    try:
        # В режиме разработки пропускаем проверку подписи
        if settings.TESTING or not settings.VERIFY_TELEGRAM_SIGNATURE:
            print(f"🔧 Режим разработки: пропускаем проверку подписи для пользователя {user_id}")
        
        # Создаем или обновляем пользователя
        full_name = f"{first_name} {last_name}".strip()
        db_user_id = user_repository.add_user(user_id, full_name, username)
        
        if not db_user_id:
            # Пользователь уже существует, получаем его ID
            db_user_id = user_repository.resolve_user_id(user_id)
        
        # Получаем личный проект пользователя
        personal_project_id = user_repository.get_user_personal_project_id(db_user_id)
        
        # Получаем данные пользователя
        user_data = {
            "id": db_user_id,  # ✅ Правильный database ID
            "telegram_id": user_id,  # Telegram ID для обратной совместимости
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "photo_url": photo_url,
            "full_name": full_name,
            "personal_project_id": personal_project_id
        }
        
        print(f"✅ Пользователь авторизован: {user_data}")
        
        return {
            "status": "ok",
            "user": user_data,
            "message": "Авторизация успешна"
        }
        
    except Exception as e:
        print(f"❌ Ошибка авторизации: {e}")
        raise HTTPException(status_code=500, detail=f"Error during authorization: {str(e)}")