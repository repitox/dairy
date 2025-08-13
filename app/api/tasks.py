"""
API для работы с задачами
"""
from fastapi import APIRouter, Request, HTTPException
from app.database.repositories.task_repository import task_repository

router = APIRouter()


@router.get("/tasks")
async def get_tasks(user_id: int, completed: bool = None):
    """Получить задачи пользователя"""
    try:
        tasks = task_repository.get_user_tasks(user_id, completed)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tasks: {str(e)}")


@router.post("/tasks")
async def add_task(request: Request):
    """Добавить новую задачу"""
    data = await request.json()
    title = data.get("title")
    description = data.get("description")
    due_date = data.get("due_date")
    priority = data.get("priority", "обычная")
    user_id = data.get("user_id")

    if not title or not user_id:
        raise HTTPException(status_code=400, detail="title and user_id required")

    try:
        task_id = task_repository.add_task(user_id, title, description, due_date, priority)
        return {"status": "ok", "id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding task: {str(e)}")


@router.put("/tasks/{task_id}")
async def update_task(task_id: int, request: Request):
    """Обновить задачу"""
    data = await request.json()
    user_id = data.get("user_id")
    title = data.get("title")
    description = data.get("description")
    due_date = data.get("due_date")
    priority = data.get("priority", "обычная")

    if not user_id or not title:
        raise HTTPException(status_code=400, detail="user_id and title required")

    try:
        success = task_repository.update_task(task_id, user_id, title, description, due_date, priority)
        if success:
            return {"status": "ok"}
        else:
            raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")


@router.post("/tasks/{task_id}/toggle")
async def toggle_task(task_id: int, request: Request):
    """Переключить статус выполнения задачи"""
    data = await request.json()
    user_id = data.get("user_id")

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id required")

    try:
        success = task_repository.toggle_task_completion(task_id, user_id)
        if success:
            return {"status": "ok"}
        else:
            raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error toggling task: {str(e)}")


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int, request: Request):
    """Удалить задачу"""
    data = await request.json()
    user_id = data.get("user_id")

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id required")

    try:
        success = task_repository.delete_task(task_id, user_id)
        if success:
            return {"status": "ok"}
        else:
            raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting task: {str(e)}")


@router.get("/tasks/overdue")
async def get_overdue_tasks(user_id: int):
    """Получить просроченные задачи"""
    try:
        tasks = task_repository.get_overdue_tasks(user_id)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching overdue tasks: {str(e)}")


@router.get("/tasks/priority/{priority}")
async def get_tasks_by_priority(priority: str, user_id: int):
    """Получить задачи по приоритету"""
    try:
        tasks = task_repository.get_tasks_by_priority(user_id, priority)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tasks by priority: {str(e)}")