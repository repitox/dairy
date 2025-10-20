"""
API для работы с событиями
"""
from fastapi import APIRouter, Request, HTTPException
from app.database.repositories.event_repository import event_repository
from app.database.repositories.user_repository import user_repository
from app.utils.datetime_utils import parse_datetime_string, format_datetime_for_user

router = APIRouter()


@router.get("/events")
async def get_events(user_id: int, active_only: bool = True):
    """Получить события пользователя"""
    try:
        events = event_repository.get_user_events(user_id, active_only)
        
        # Получаем часовой пояс пользователя
        user_timezone = user_repository.get_user_setting(user_id, "timezone") or "0"
        
        # Конвертируем даты для отображения пользователю
        for event in events:
            if event.get('start_at'):
                try:
                    from datetime import datetime
                    utc_start = datetime.fromisoformat(event['start_at'].replace('Z', ''))
                    event['start_at_display'] = format_datetime_for_user(utc_start, user_timezone, "full")
                    event['start_at_date'] = format_datetime_for_user(utc_start, user_timezone, "date")
                    event['start_at_time'] = format_datetime_for_user(utc_start, user_timezone, "time")
                except Exception as e:
                    print(f"Ошибка конвертации start_at события {event.get('id')}: {e}")
                    event['start_at_display'] = event['start_at']
            
            if event.get('end_at'):
                try:
                    from datetime import datetime
                    utc_end = datetime.fromisoformat(event['end_at'].replace('Z', ''))
                    event['end_at_display'] = format_datetime_for_user(utc_end, user_timezone, "full")
                    event['end_at_date'] = format_datetime_for_user(utc_end, user_timezone, "date")
                    event['end_at_time'] = format_datetime_for_user(utc_end, user_timezone, "time")
                except Exception as e:
                    print(f"Ошибка конвертации end_at события {event.get('id')}: {e}")
                    event['end_at_display'] = event['end_at']
        
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching events: {str(e)}")


@router.post("/events")
async def add_event(request: Request):
    """Добавить новое событие"""
    data = await request.json()
    title = data.get("title")
    location = data.get("location")
    start_at = data.get("start_at")
    end_at = data.get("end_at")
    user_id = data.get("user_id")
    description = data.get("description")

    if not all([title, location, start_at, end_at, user_id]):
        raise HTTPException(status_code=400, detail="title, location, start_at, end_at, and user_id required")

    try:
        # Получаем часовой пояс пользователя
        user_timezone = user_repository.get_user_setting(user_id, "timezone") or "0"
        
        # Конвертируем даты из пользовательского часового пояса в UTC
        utc_start_at = None
        utc_end_at = None
        
        if start_at:
            try:
                utc_start_datetime = parse_datetime_string(start_at, user_timezone)
                utc_start_at = utc_start_datetime.isoformat() if utc_start_datetime else start_at
            except Exception as e:
                print(f"Ошибка конвертации start_at при создании события: {e}")
                utc_start_at = start_at
        
        if end_at:
            try:
                utc_end_datetime = parse_datetime_string(end_at, user_timezone)
                utc_end_at = utc_end_datetime.isoformat() if utc_end_datetime else end_at
            except Exception as e:
                print(f"Ошибка конвертации end_at при создании события: {e}")
                utc_end_at = end_at
        
        event_id = event_repository.add_event(user_id, title, location, utc_start_at, utc_end_at, description)
        return {"status": "ok", "id": event_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding event: {str(e)}")


# ===== КОНКРЕТНЫЕ МАРШРУТЫ (должны быть ДО универсальных с {event_id}) =====

@router.get("/events/today")
async def get_today_events(user_id: int):
    """Получить события на сегодня"""
    try:
        events = event_repository.get_today_events(user_id)
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching today events: {str(e)}")


@router.get("/events/upcoming")
async def get_upcoming_events(user_id: int, hours_ahead: int = 24):
    """Получить предстоящие события"""
    try:
        events = event_repository.get_upcoming_events(user_id, hours_ahead)
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching upcoming events: {str(e)}")


# ===== УНИВЕРСАЛЬНЫЕ МАРШРУТЫ С ПАРАМЕТРАМИ (должны быть ПОСЛЕ конкретных) =====

@router.put("/events/{event_id}")
async def update_event(event_id: int, request: Request):
    """Обновить событие"""
    data = await request.json()
    user_id = data.get("user_id")
    title = data.get("title")
    location = data.get("location")
    start_at = data.get("start_at")
    end_at = data.get("end_at")
    description = data.get("description")

    if not all([user_id, title, location, start_at, end_at]):
        raise HTTPException(status_code=400, detail="user_id, title, location, start_at, and end_at required")

    try:
        # Получаем часовой пояс пользователя
        user_timezone = user_repository.get_user_setting(user_id, "timezone") or "0"
        
        # Конвертируем даты из пользовательского часового пояса в UTC
        utc_start_at = None
        utc_end_at = None
        
        if start_at:
            try:
                utc_start_datetime = parse_datetime_string(start_at, user_timezone)
                utc_start_at = utc_start_datetime.isoformat() if utc_start_datetime else start_at
            except Exception as e:
                print(f"Ошибка конвертации start_at при обновлении события: {e}")
                utc_start_at = start_at
        
        if end_at:
            try:
                utc_end_datetime = parse_datetime_string(end_at, user_timezone)
                utc_end_at = utc_end_datetime.isoformat() if utc_end_datetime else end_at
            except Exception as e:
                print(f"Ошибка конвертации end_at при обновлении события: {e}")
                utc_end_at = end_at
        
        success = event_repository.update_event(event_id, user_id, title, location, utc_start_at, utc_end_at, description)
        if success:
            return {"status": "ok"}
        else:
            raise HTTPException(status_code=404, detail="Event not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating event: {str(e)}")


@router.delete("/events/{event_id}")
async def delete_event(event_id: int, request: Request):
    """Удалить событие"""
    data = await request.json()
    user_id = data.get("user_id")

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id required")

    try:
        success = event_repository.delete_event(event_id, user_id)
        if success:
            return {"status": "ok"}
        else:
            raise HTTPException(status_code=404, detail="Event not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting event: {str(e)}")