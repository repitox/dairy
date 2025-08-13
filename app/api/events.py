"""
API для работы с событиями
"""
from fastapi import APIRouter, Request, HTTPException
from app.database.repositories.event_repository import event_repository

router = APIRouter()


@router.get("/events")
async def get_events(user_id: int, active_only: bool = True):
    """Получить события пользователя"""
    try:
        events = event_repository.get_user_events(user_id, active_only)
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
        event_id = event_repository.add_event(user_id, title, location, start_at, end_at, description)
        return {"status": "ok", "id": event_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding event: {str(e)}")


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
        success = event_repository.update_event(event_id, user_id, title, location, start_at, end_at, description)
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


@router.get("/events/upcoming")
async def get_upcoming_events(user_id: int, hours_ahead: int = 24):
    """Получить предстоящие события"""
    try:
        events = event_repository.get_upcoming_events(user_id, hours_ahead)
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching upcoming events: {str(e)}")