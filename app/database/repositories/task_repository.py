"""
Репозиторий для работы с задачами
"""
from typing import List, Optional
from datetime import datetime

from app.database.connection import get_db_cursor
from app.database.models.task import Task
from app.database.repositories.user_repository import user_repository


class TaskRepository:
    """Репозиторий для работы с задачами"""
    
    def add_task(self, user_id: int, title: str, description: Optional[str] = None,
                 due_date: Optional[str] = None, priority: str = "обычная") -> Optional[int]:
        """Добавить новую задачу"""
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            print(f"❌ Пользователь с ID {user_id} не найден")
            return None
        
        # Получаем проект пользователя
        project_id = user_repository.get_user_personal_project_id(db_user_id)
        
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO tasks (user_id, project_id, title, description, due_date, 
                                 priority, completed, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (db_user_id, project_id, title, description, due_date, 
                  priority, False, datetime.utcnow().isoformat()))
            
            result = cur.fetchone()
            task_id = result['id']
            print(f"✅ Задача создана с ID {task_id} для пользователя {db_user_id}")
            return task_id
    
    def get_user_tasks(self, user_id: int, completed: Optional[bool] = None) -> List[dict]:
        """Получить задачи пользователя"""
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            return []
        
        with get_db_cursor() as cur:
            if completed is None:
                cur.execute("""
                    SELECT * FROM tasks 
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                """, (db_user_id,))
            else:
                cur.execute("""
                    SELECT * FROM tasks 
                    WHERE user_id = %s AND completed = %s
                    ORDER BY created_at DESC
                """, (db_user_id, completed))
            return cur.fetchall()
    
    def get_task(self, task_id: int, user_id: int) -> Optional[dict]:
        """Получить одну конкретную задачу по ID"""
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT * FROM tasks 
                WHERE id = %s AND user_id = %s
            """, (task_id, user_id))
            return cur.fetchone()
    
    def toggle_task_completion(self, task_id: int, user_id: int) -> bool:
        """Переключить статус выполнения задачи"""
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            return False
        
        with get_db_cursor() as cur:
            # Получаем текущий статус
            cur.execute("SELECT completed FROM tasks WHERE id = %s AND user_id = %s", 
                       (task_id, db_user_id))
            result = cur.fetchone()
            if not result:
                return False
            
            new_status = not result['completed']
            completed_at = datetime.utcnow().isoformat() if new_status else None
            
            cur.execute("""
                UPDATE tasks 
                SET completed = %s, completed_at = %s 
                WHERE id = %s AND user_id = %s
            """, (new_status, completed_at, task_id, db_user_id))
            return True
    
    def update_task(self, task_id: int, user_id: int, title: str, 
                   description: Optional[str] = None, due_date: Optional[str] = None,
                   priority: str = "обычная") -> bool:
        """Обновить задачу"""
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            return False
        
        with get_db_cursor() as cur:
            cur.execute("""
                UPDATE tasks 
                SET title = %s, description = %s, due_date = %s, priority = %s
                WHERE id = %s AND user_id = %s
            """, (title, description, due_date, priority, task_id, db_user_id))
            return cur.rowcount > 0
    
    def delete_task(self, task_id: int, user_id: int) -> bool:
        """Удалить задачу"""
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            return False
        
        with get_db_cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id = %s AND user_id = %s", 
                       (task_id, db_user_id))
            return cur.rowcount > 0
    
    def get_overdue_tasks(self, user_id: int) -> List[dict]:
        """Получить просроченные задачи"""
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            return []
        
        today = datetime.utcnow().date().isoformat()
        
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT * FROM tasks 
                WHERE user_id = %s AND completed = FALSE 
                AND due_date IS NOT NULL AND due_date < %s
                ORDER BY due_date ASC
            """, (db_user_id, today))
            return cur.fetchall()
    
    def get_tasks_by_priority(self, user_id: int, priority: str) -> List[dict]:
        """Получить задачи по приоритету"""
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            return []
        
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT * FROM tasks 
                WHERE user_id = %s AND priority = %s AND completed = FALSE
                ORDER BY created_at DESC
            """, (db_user_id, priority))
            return cur.fetchall()
    
    def get_today_tasks(self, user_id: int) -> dict:
        """Получить задачи на сегодня (разделено на переросших и на сегодня)"""
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            return {"today": [], "overdue": []}
        
        today = datetime.utcnow().date().isoformat()
        
        with get_db_cursor() as cur:
            # Задачи на сегодня
            cur.execute("""
                SELECT * FROM tasks 
                WHERE user_id = %s AND completed = FALSE 
                AND due_date = %s
                ORDER BY created_at DESC
            """, (db_user_id, today))
            today_tasks = cur.fetchall()
            
            # Просроченные задачи (раньше сегодня)
            cur.execute("""
                SELECT * FROM tasks 
                WHERE user_id = %s AND completed = FALSE 
                AND due_date IS NOT NULL AND due_date < %s
                ORDER BY due_date ASC
            """, (db_user_id, today))
            overdue_tasks = cur.fetchall()
        
        return {"today": today_tasks, "overdue": overdue_tasks}


# Создаем экземпляр репозитория
task_repository = TaskRepository()