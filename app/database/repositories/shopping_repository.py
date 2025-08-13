"""
Репозиторий для работы с покупками
"""
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from app.database.connection import get_db_cursor
from app.database.models.shopping import Purchase, ShoppingList
from app.database.repositories.user_repository import user_repository


class ShoppingRepository:
    """Репозиторий для работы с покупками"""
    
    def add_shopping_item(self, user_id: int, name: str, quantity: int = 1, 
                         price: Optional[Decimal] = None, category: str = "other",
                         shopping_list_id: Optional[int] = None, url: Optional[str] = None,
                         comment: Optional[str] = None) -> Optional[int]:
        """Добавить новый товар в список покупок"""
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            print(f"❌ Пользователь с ID {user_id} не найден")
            return None
        
        # Получаем проект пользователя
        project_id = user_repository.get_user_personal_project_id(db_user_id)
        
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO purchases (user_id, project_id, name, quantity, price, category, 
                                     shopping_list_id, url, comment, completed, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (db_user_id, project_id, name, quantity, price, category, 
                  shopping_list_id, url, comment, False, datetime.utcnow().isoformat()))
            
            result = cur.fetchone()
            item_id = result['id']
            print(f"✅ Товар создан с ID {item_id} для пользователя {db_user_id}")
            return item_id
    
    def get_shopping_items(self, user_id: int) -> List[dict]:
        """Получить список покупок пользователя"""
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            return []
        
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT p.*, sl.name as list_name
                FROM purchases p
                LEFT JOIN shopping_lists sl ON p.shopping_list_id = sl.id
                WHERE p.user_id = %s
                ORDER BY p.created_at DESC
            """, (db_user_id,))
            return cur.fetchall()
    
    def toggle_shopping_item(self, item_id: int, user_id: int) -> bool:
        """Переключить статус покупки (куплено/не куплено)"""
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            return False
        
        with get_db_cursor() as cur:
            # Сначала получаем текущий статус
            cur.execute("SELECT completed FROM purchases WHERE id = %s AND user_id = %s", 
                       (item_id, db_user_id))
            result = cur.fetchone()
            if not result:
                return False
            
            new_status = not result['completed']
            cur.execute("UPDATE purchases SET completed = %s WHERE id = %s AND user_id = %s", 
                       (new_status, item_id, db_user_id))
            return True
    
    def update_shopping_item(self, item_id: int, user_id: int, name: str, 
                           quantity: int = 1, price: Optional[Decimal] = None,
                           category: str = "other", shopping_list_id: Optional[int] = None,
                           url: Optional[str] = None, comment: Optional[str] = None) -> bool:
        """Обновить товар в списке покупок"""
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            return False
        
        with get_db_cursor() as cur:
            cur.execute("""
                UPDATE purchases 
                SET name = %s, quantity = %s, price = %s, category = %s,
                    shopping_list_id = %s, url = %s, comment = %s
                WHERE id = %s AND user_id = %s
            """, (name, quantity, price, category, shopping_list_id, url, comment, item_id, db_user_id))
            return cur.rowcount > 0
    
    def delete_shopping_item(self, item_id: int, user_id: int) -> bool:
        """Удалить товар из списка покупок"""
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            return False
        
        with get_db_cursor() as cur:
            cur.execute("DELETE FROM purchases WHERE id = %s AND user_id = %s", 
                       (item_id, db_user_id))
            return cur.rowcount > 0
    
    def get_recent_purchases(self, user_id: int, limit: int = 5) -> List[dict]:
        """Получить последние покупки пользователя"""
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            return []
        
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT * FROM purchases 
                WHERE user_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (db_user_id, limit))
            return cur.fetchall()
    
    # Методы для работы со списками покупок
    def create_shopping_list(self, name: str, user_id: int, project_id: Optional[int] = None) -> Optional[int]:
        """Создать новый список покупок"""
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            return None
        
        if not project_id:
            project_id = user_repository.get_user_personal_project_id(db_user_id)
        
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO shopping_lists (name, project_id, user_id, created_at, active)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (name, project_id, db_user_id, datetime.utcnow().isoformat(), True))
            
            result = cur.fetchone()
            return result['id']
    
    def get_user_shopping_lists(self, user_id: int) -> List[dict]:
        """Получить списки покупок пользователя"""
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            return []
        
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT sl.*, COUNT(p.id) as items_count
                FROM shopping_lists sl
                LEFT JOIN purchases p ON sl.id = p.shopping_list_id AND p.completed = FALSE
                WHERE sl.user_id = %s AND sl.active = TRUE
                GROUP BY sl.id, sl.name, sl.created_at
                ORDER BY sl.created_at DESC
            """, (db_user_id,))
            return cur.fetchall()


# Создаем экземпляр репозитория
shopping_repository = ShoppingRepository()