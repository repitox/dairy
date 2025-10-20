"""
Репозиторий для работы с заметками
"""
from typing import List, Optional
from datetime import datetime

from app.database.connection import get_db_cursor
from app.database.repositories.user_repository import user_repository


class NotesRepository:
    """Репозиторий для работы с заметками"""
    
    def add_note(self, user_id: int, title: str, content: str) -> Optional[int]:
        """Добавить новую заметку"""
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            print(f"❌ Пользователь с ID {user_id} не найден")
            return None
        
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO notes (user_id, title, content, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (db_user_id, title, content, datetime.utcnow().isoformat(), 
                  datetime.utcnow().isoformat()))
            
            result = cur.fetchone()
            note_id = result['id']
            print(f"✅ Заметка создана с ID {note_id} для пользователя {db_user_id}")
            return note_id
    
    def get_user_notes(self, user_id: int, limit: Optional[int] = None) -> List[dict]:
        """Получить заметки пользователя"""
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            return []
        
        with get_db_cursor() as cur:
            if limit:
                cur.execute("""
                    SELECT * FROM notes 
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (db_user_id, limit))
            else:
                cur.execute("""
                    SELECT * FROM notes 
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                """, (db_user_id,))
            return cur.fetchall()
    
    def get_note(self, note_id: int, user_id: int) -> Optional[dict]:
        """Получить одну конкретную заметку по ID"""
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            return None
        
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT * FROM notes 
                WHERE id = %s AND user_id = %s
            """, (note_id, db_user_id))
            return cur.fetchone()
    
    def update_note(self, note_id: int, user_id: int, title: str, content: str) -> bool:
        """Обновить заметку"""
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            return False
        
        with get_db_cursor() as cur:
            cur.execute("""
                UPDATE notes 
                SET title = %s, content = %s, updated_at = %s
                WHERE id = %s AND user_id = %s
            """, (title, content, datetime.utcnow().isoformat(), note_id, db_user_id))
            return cur.rowcount > 0
    
    def delete_note(self, note_id: int, user_id: int) -> bool:
        """Удалить заметку"""
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            return False
        
        with get_db_cursor() as cur:
            cur.execute("DELETE FROM notes WHERE id = %s AND user_id = %s", 
                       (note_id, db_user_id))
            return cur.rowcount > 0


# Создаем экземпляр репозитория
notes_repository = NotesRepository()