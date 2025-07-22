#!/usr/bin/env python3
"""
Простая миграция для создания личных проектов
Работает с текущей структурой БД без изменения схемы
"""

from db import get_conn
from datetime import datetime

def create_personal_projects():
    """
    Создает проект "Личное" для всех пользователей, используя текущую структуру БД
    """
    print("🔄 Создаем личные проекты для всех пользователей...")
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            try:
                # Получаем всех пользователей из текущей структуры
                cur.execute("SELECT user_id, first_name FROM users ORDER BY user_id")
                users = cur.fetchall()
                
                print(f"📊 Найдено пользователей: {len(users)}")
                
                created_count = 0
                existing_count = 0
                
                for user in users:
                    telegram_id = user['user_id']  # в текущей структуре это telegram_id
                    first_name = user['first_name']
                    
                    # Проверяем, есть ли уже личный проект
                    # В текущей структуре projects.owner_id ссылается на users.user_id (telegram_id)
                    cur.execute("""
                        SELECT id FROM projects 
                        WHERE owner_id = %s AND name = 'Личное' AND active = TRUE
                    """, (telegram_id,))
                    
                    if cur.fetchone():
                        print(f"✅ У пользователя {first_name} уже есть личный проект")
                        existing_count += 1
                        continue
                    
                    # Создаем личный проект
                    cur.execute("""
                        INSERT INTO projects (name, owner_id, color, created_at, active)
                        VALUES ('Личное', %s, '#6366f1', %s, TRUE)
                        RETURNING id;
                    """, (telegram_id, datetime.utcnow().isoformat()))
                    
                    project_result = cur.fetchone()
                    personal_project_id = project_result['id']
                    
                    print(f"✅ Создан личный проект для {first_name} (telegram_id: {telegram_id}) -> проект ID: {personal_project_id}")
                    created_count += 1
                
                conn.commit()
                
                print(f"\n🎉 Создание личных проектов завершено!")
                print(f"📊 Создано новых проектов: {created_count}")
                print(f"📊 Уже существовало: {existing_count}")
                print(f"📊 Всего пользователей: {len(users)}")
                
                # Проверяем результат
                cur.execute("""
                    SELECT COUNT(*) as total_users,
                           COUNT(p.id) as users_with_personal_projects
                    FROM users u
                    LEFT JOIN projects p ON u.user_id = p.owner_id AND p.name = 'Личное' AND p.active = TRUE
                """)
                result = cur.fetchone()
                
                print(f"\n🔍 Проверка:")
                print(f"Всего пользователей: {result['total_users']}")
                print(f"С личными проектами: {result['users_with_personal_projects']}")
                
                if result['total_users'] == result['users_with_personal_projects']:
                    print("🎉 Все пользователи теперь имеют личные проекты!")
                else:
                    print("⚠️  Не у всех пользователей есть личные проекты.")
                
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                conn.rollback()
                raise

if __name__ == "__main__":
    create_personal_projects()