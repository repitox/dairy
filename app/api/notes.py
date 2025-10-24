"""
API для работы с заметками
"""
from fastapi import APIRouter, Request, HTTPException
from app.database.repositories.notes_repository import notes_repository

router = APIRouter()


@router.get("/notes")
async def get_notes(user_id: int, limit: int = None):
    """Получить заметки пользователя"""
    try:
        notes = notes_repository.get_user_notes(user_id, limit)
        return notes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching notes: {str(e)}")


@router.get("/notes/{note_id}")
async def get_note(note_id: int, user_id: int):
    """Получить одну заметку по ID"""
    try:
        note = notes_repository.get_note(note_id, user_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return note
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching note: {str(e)}")


@router.post("/notes")
async def add_note(request: Request):
    """Добавить новую заметку"""
    data = await request.json()
    title = data.get("title")
    content = data.get("content")
    user_id = data.get("user_id")

    if not all([title, content, user_id]):
        raise HTTPException(status_code=400, detail="title, content, and user_id required")

    try:
        note_id = notes_repository.add_note(user_id, title, content)
        return {"status": "ok", "id": note_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding note: {str(e)}")


@router.put("/notes/{note_id}")
async def update_note(note_id: int, request: Request):
    """Обновить заметку"""
    data = await request.json()
    user_id = data.get("user_id")
    title = data.get("title")
    content = data.get("content")

    if not all([user_id, title, content]):
        raise HTTPException(status_code=400, detail="user_id, title, and content required")

    try:
        success = notes_repository.update_note(note_id, user_id, title, content)
        if success:
            return {"status": "ok"}
        else:
            raise HTTPException(status_code=404, detail="Note not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating note: {str(e)}")


@router.delete("/notes/{note_id}")
async def delete_note(note_id: int, request: Request):
    """Удалить заметку"""
    data = await request.json()
    user_id = data.get("user_id")

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id required")

    try:
        success = notes_repository.delete_note(note_id, user_id)
        if success:
            return {"status": "ok"}
        else:
            raise HTTPException(status_code=404, detail="Note not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting note: {str(e)}")