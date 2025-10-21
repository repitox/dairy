"""
API для работы с задачами
"""
from fastapi import APIRouter, Request, HTTPException
from app.database.repositories.task_repository import task_repository
from app.database.repositories.user_repository import user_repository
from app.utils.datetime_utils import parse_datetime_string, format_datetime_for_user

router = APIRouter()


@router.get("/tasks")
async def get_tasks(user_id: int, completed: bool = None):
    """Получить задачи пользователя"""
    try:
        tasks = task_repository.get_user_tasks(user_id, completed)
        
        # Получаем часовой пояс пользователя
        user_timezone = user_repository.get_user_setting(user_id, "timezone") or "0"
        
        # Конвертируем даты для отображения пользователю
        for task in tasks:
            if task.get('due_date'):
                try:
                    # Парсим UTC дату из БД и конвертируем в пользовательский часовой пояс
                    from datetime import datetime
                    utc_date = datetime.fromisoformat(task['due_date'].replace('Z', ''))
                    task['due_date_display'] = format_datetime_for_user(utc_date, user_timezone, "full")
                    task['due_date_relative'] = format_datetime_for_user(utc_date, user_timezone, "relative")
                except Exception as e:
                    print(f"Ошибка конвертации даты задачи {task.get('id')}: {e}")
                    task['due_date_display'] = task['due_date']
                    task['due_date_relative'] = task['due_date']
        
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
        # Конвертируем дату из пользовательского часового пояса в UTC
        utc_due_date = None
        if due_date:
            user_timezone = user_repository.get_user_setting(user_id, "timezone") or "0"
            try:
                utc_datetime = parse_datetime_string(due_date, user_timezone)
                utc_due_date = utc_datetime.isoformat() if utc_datetime else None
            except Exception as e:
                print(f"Ошибка конвертации даты при создании задачи: {e}")
                utc_due_date = due_date  # Fallback к исходной дате
        
        task_id = task_repository.add_task(user_id, title, description, utc_due_date, priority)
        return {"status": "ok", "id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding task: {str(e)}")


# ===== КОНКРЕТНЫЕ МАРШРУТЫ (должны быть ДО универсальных с {task_id}) =====

@router.get("/tasks/today")
async def get_today_tasks(user_id: int):
    """Получить задачи на сегодня (разделено на переросших и на сегодня)"""
    try:
        tasks = task_repository.get_today_tasks(user_id)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching today tasks: {str(e)}")


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


# ===== УНИВЕРСАЛЬНЫЕ МАРШРУТЫ С ПАРАМЕТРАМИ (должны быть ПОСЛЕ конкретных) =====

@router.get("/tasks/{task_id}")
async def get_task(task_id: int, user_id: int):
    """Получить одну конкретную задачу"""
    try:
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        task = task_repository.get_task(task_id, db_user_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Получаем часовой пояс пользователя
        user_timezone = user_repository.get_user_setting(db_user_id, "timezone") or "0"
        
        # Конвертируем даты для отображения пользователю
        if task.get('due_date'):
            try:
                from datetime import datetime
                utc_date = datetime.fromisoformat(task['due_date'].replace('Z', ''))
                task['due_date_display'] = format_datetime_for_user(utc_date, user_timezone, "full")
                task['due_date_relative'] = format_datetime_for_user(utc_date, user_timezone, "relative")
            except Exception as e:
                print(f"Ошибка конвертации даты задачи {task.get('id')}: {e}")
                task['due_date_display'] = task['due_date']
                task['due_date_relative'] = task['due_date']
        
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching task: {str(e)}")


@router.put("/tasks/{task_id}")
async def update_task(task_id: int, request: Request, user_id: int = None):
    """Обновить задачу"""
    data = await request.json()
    
    # ✅ Поддержка user_id из query параметров или body
    if not user_id:
        user_id = data.get("user_id")
    
    title = data.get("title")
    description = data.get("description")
    due_date = data.get("due_date")
    priority = data.get("priority", "обычная")

    if not user_id or not title:
        raise HTTPException(status_code=400, detail="user_id and title required")

    try:
        # Конвертируем дату из пользовательского часового пояса в UTC
        utc_due_date = None
        if due_date:
            user_timezone = user_repository.get_user_setting(user_id, "timezone") or "0"
            try:
                utc_datetime = parse_datetime_string(due_date, user_timezone)
                utc_due_date = utc_datetime.isoformat() if utc_datetime else None
            except Exception as e:
                print(f"Ошибка конвертации даты при обновлении задачи: {e}")
                utc_due_date = due_date  # Fallback к исходной дате
        
        success = task_repository.update_task(task_id, user_id, title, description, utc_due_date, priority)
        if success:
            return {"status": "ok"}
        else:
            raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")


@router.post("/tasks/{task_id}/toggle")
async def toggle_task(task_id: int, request: Request, user_id: int = None):
    """Переключить статус выполнения задачи"""
    data = await request.json()
    
    # ✅ Поддержка user_id из query параметров или body
    if not user_id:
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
async def delete_task(task_id: int, request: Request, user_id: int = None):
    """Удалить задачу"""
    data = await request.json()
    
    # ✅ Поддержка user_id из query параметров или body
    if not user_id:
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