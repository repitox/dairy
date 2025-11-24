"""
Репозиторий для работы с пользователями
"""
from typing import Optional, Dict
from datetime import datetime
import psycopg2.extras

from app.database.connection import get_db_cursor
from app.database.models.user import User, UserSetting


class UserRepository:
    """Репозиторий для работы с пользователями"""
    
    def add_user(self, telegram_id: int, first_name: str, username: str) -> Optional[int]:
        """
        Добавляет пользователя в БД с новой структурой после миграции.
        telegram_id - это telegram_id пользователя
        """
        print(f"🗄 Добавляем пользователя: {telegram_id}, {first_name}, {username}")
        
        with get_db_cursor() as cur:
            try:
                # Вставляем пользователя с новой структурой
                cur.execute("""
                    INSERT INTO users (telegram_id, first_name, username, registered_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (telegram_id) DO NOTHING
                    RETURNING id;
                """, (telegram_id, first_name, username, datetime.utcnow().isoformat()))
                
                # Получаем ID пользователя (новый автоинкрементный или существующий)
                result = cur.fetchone()
                if result:
                    internal_user_id = result['id']
                    print(f"✅ Создан новый пользователь с id={internal_user_id}")
                else:
                    # Пользователь уже существует, получаем его ID
                    cur.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
                    internal_user_id = cur.fetchone()['id']
                    print(f"✅ Пользователь уже существует с id={internal_user_id}")
                
                # Создаем личный проект для пользователя, используя внутренний ID
                self._create_personal_project_if_not_exists(cur, internal_user_id)
                
                print("✅ Пользователь добавлен (или уже существует)")
                return internal_user_id
            except Exception as e:
                print("❌ Ошибка при добавлении пользователя:", e)
                return None
    
    def _create_personal_project_if_not_exists(self, cur, internal_user_id: int):
        """Создает личный проект для пользователя, если его нет"""
        # Сначала проверяем, существует ли проект
        cur.execute("SELECT id FROM projects WHERE owner_id = %s AND name = 'Личное'", (internal_user_id,))
        existing_project = cur.fetchone()
        
        if existing_project:
            personal_project_id = existing_project['id']
            print(f"✅ Личный проект уже существует с ID {personal_project_id}")
        else:
            # Создаем новый проект
            cur.execute("""
                INSERT INTO projects (name, owner_id, color, created_at, active)
                VALUES ('Личное', %s, '#6366f1', %s, TRUE)
                RETURNING id;
            """, (internal_user_id, datetime.utcnow().isoformat()))
            
            project_result = cur.fetchone()
            personal_project_id = project_result['id']
            print(f"✅ Создан новый личный проект с ID {personal_project_id}")
        
        # Добавляем пользователя как участника своего личного проекта
        cur.execute("""
            INSERT INTO project_members (project_id, user_id, joined_at)
            VALUES (%s, %s, %s)
            ON CONFLICT (project_id, user_id) DO NOTHING;
        """, (personal_project_id, internal_user_id, datetime.utcnow().isoformat()))
    
    def get_user_personal_project_id(self, internal_user_id: int) -> Optional[int]:
        """Получить ID личного проекта пользователя по внутреннему ID пользователя"""
        with get_db_cursor() as cur:
            # Ищем проект по внутреннему ID пользователя (projects.owner_id = users.id)
            cur.execute("""
                SELECT id FROM projects 
                WHERE owner_id = %s AND name = 'Личное' AND active = TRUE
                LIMIT 1
            """, (internal_user_id,))
            result = cur.fetchone()
            return result['id'] if result else None
    
    def get_user_db_id(self, telegram_id: int) -> Optional[int]:
        """Получить ID пользователя из БД по telegram_id"""
        with get_db_cursor() as cur:
            cur.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
            result = cur.fetchone()
            return result['id'] if result else None
    
    def resolve_user_id(self, user_id: int) -> Optional[int]:
        """
        Умная функция для получения внутреннего ID пользователя.
        Сначала проверяет, является ли user_id уже внутренним ID (малое число),
        если нет - ищет по telegram_id (большое число).
        """
        with get_db_cursor() as cur:
            # Если user_id маленький (< 1000000), возможно это уже ID из БД
            if user_id < 1000000:
                # Проверяем, существует ли пользователь с таким ID
                cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
                result = cur.fetchone()
                if result:
                    return result['id']
            
            # Если не найден как ID из БД или user_id большой, ищем по telegram_id
            cur.execute("SELECT id FROM users WHERE telegram_id = %s", (user_id,))
            result = cur.fetchone()
            return result['id'] if result else None
    
    def update_user_setting(self, user_id: int, key: str, value: str):
        """Обновляет настройку пользователя. user_id может быть telegram_id или ID из БД."""
        db_user_id = self.resolve_user_id(user_id)
        if not db_user_id:
            print(f"❌ Пользователь с ID {user_id} не найден")
            return
            
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO user_settings (user_id, key, value)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, key) DO UPDATE SET value = EXCLUDED.value;
            """, (db_user_id, key, value))
            print(f"✅ Настройка {key}={value} обновлена для пользователя {db_user_id}")
    
    def get_user_settings(self, user_id: int) -> Dict[str, str]:
        """Получить все настройки пользователя"""
        db_user_id = self.resolve_user_id(user_id)
        if not db_user_id:
            return {}
            
        with get_db_cursor() as cur:
            cur.execute("SELECT key, value FROM user_settings WHERE user_id = %s", (db_user_id,))
            results = cur.fetchall()
            return {row['key']: row['value'] for row in results}
    
    def get_user_setting(self, user_id: int, key: str) -> Optional[str]:
        """Получить конкретную настройку пользователя по ключу"""
        db_user_id = self.resolve_user_id(user_id)
        if not db_user_id:
            return None
            
        with get_db_cursor() as cur:
            cur.execute("SELECT value FROM user_settings WHERE user_id = %s AND key = %s", (db_user_id, key))
            result = cur.fetchone()
            return result['value'] if result else None
    
    def get_user_projects(self, user_id: int) -> list:
        """Получить список всех проектов, где пользователь участник"""
        db_user_id = self.resolve_user_id(user_id)
        if not db_user_id:
            return []
        
        with get_db_cursor() as cur:
            # Получаем все проекты, в которых пользователь участник
            cur.execute("""
                SELECT 
                    p.id,
                    p.name,
                    p.owner_id,
                    p.color,
                    p.created_at,
                    p.active
                FROM projects p
                INNER JOIN project_members pm ON p.id = pm.project_id
                WHERE pm.user_id = %s AND p.active = TRUE
                ORDER BY p.name ASC
            """, (db_user_id,))
            results = cur.fetchall()
            return [
                {
                    'id': row['id'],
                    'name': row['name'],
                    'owner_id': row['owner_id'],
                    'color': row['color'],
                    'created_at': row['created_at'],
                    'active': row['active']
                }
                for row in results
            ]
    
    def get_project_by_id(self, project_id: int) -> Optional[dict]:
        """Получить проект по ID"""
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT 
                    id,
                    name,
                    owner_id,
                    color,
                    created_at,
                    active
                FROM projects
                WHERE id = %s AND active = TRUE
            """, (project_id,))
            result = cur.fetchone()
            if result:
                return {
                    'id': result['id'],
                    'name': result['name'],
                    'owner_id': result['owner_id'],
                    'color': result['color'],
                    'created_at': result['created_at'],
                    'active': result['active']
                }
            return None


# Создаем экземпляр репозитория для использования
user_repository = UserRepository()