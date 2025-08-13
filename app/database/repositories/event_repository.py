"""
Репозиторий для работы с событиями
"""
from typing import List, Optional
from datetime import datetime

from app.database.connection import get_db_cursor
from app.database.models.event import Event
from app.database.repositories.user_repository import user_repository


class EventRepository:
    """Репозиторий для работы с событиями"""
    
    def add_event(self, user_id: int, title: str, location: str, start_at: str, 
                  end_at: str, description: Optional[str] = None) -> Optional[int]:
        """Добавить новое событие"""
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            print(f"❌ Пользователь с ID {user_id} не найден")
            return None
        
        # Получаем проект пользователя
        project_id = user_repository.get_user_personal_project_id(db_user_id)
        
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO events (user_id, project_id, title, location, start_at, end_at, 
                                  description, active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (db_user_id, project_id, title, location, start_at, end_at, 
                  description, True, datetime.utcnow().isoformat()))
            
            result = cur.fetchone()
            event_id = result['id']
            print(f"✅ Событие создано с ID {event_id} для пользователя {db_user_id}")
            return event_id
    
    def get_user_events(self, user_id: int, active_only: bool = True) -> List[dict]:
        """Получить события пользователя"""
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            return []
        
        with get_db_cursor() as cur:
            if active_only:
                cur.execute("""
                    SELECT * FROM events 
                    WHERE user_id = %s AND active = TRUE
                    ORDER BY start_at ASC
                """, (db_user_id,))
            else:
                cur.execute("""
                    SELECT * FROM events 
                    WHERE user_id = %s
                    ORDER BY start_at ASC
                """, (db_user_id,))
            return cur.fetchall()
    
    def update_event(self, event_id: int, user_id: int, title: str, location: str,
                    start_at: str, end_at: str, description: Optional[str] = None) -> bool:
        """Обновить событие"""
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            return False
        
        with get_db_cursor() as cur:
            cur.execute("""
                UPDATE events 
                SET title = %s, location = %s, start_at = %s, end_at = %s, description = %s
                WHERE id = %s AND user_id = %s
            """, (title, location, start_at, end_at, description, event_id, db_user_id))
            return cur.rowcount > 0
    
    def delete_event(self, event_id: int, user_id: int) -> bool:
        """Удалить событие (мягкое удаление)"""
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            return False
        
        with get_db_cursor() as cur:
            cur.execute("""
                UPDATE events SET active = FALSE 
                WHERE id = %s AND user_id = %s
            """, (event_id, db_user_id))
            return cur.rowcount > 0
    
    def get_upcoming_events(self, user_id: int, hours_ahead: int = 24) -> List[dict]:
        """Получить предстоящие события"""
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            return []
        
        from datetime import timedelta
        now = datetime.utcnow()
        future_time = now + timedelta(hours=hours_ahead)
        
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT * FROM events 
                WHERE user_id = %s AND active = TRUE
                AND start_at BETWEEN %s AND %s
                ORDER BY start_at ASC
            """, (db_user_id, now.isoformat(), future_time.isoformat()))
            return cur.fetchall()


# Создаем экземпляр репозитория
event_repository = EventRepository()