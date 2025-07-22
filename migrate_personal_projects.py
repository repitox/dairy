#!/usr/bin/env python3
"""
Миграция для создания проектов "Личное" для всех существующих пользователей
"""

from db import get_conn, get_user_personal_project_id
from datetime import datetime

def migrate_personal_projects():
    """
    Создает проект "Личное" для всех пользователей, у которых его нет
    """
    print("🔄 Начинаем миграцию личных проектов...")
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Получаем всех пользователей (используем правильные имена полей)
            cur.execute("SELECT user_id, first_name FROM users ORDER BY user_id")
            users = cur.fetchall()
            
            print(f"📊 Найдено пользователей: {len(users)}")
            
            created_count = 0
            existing_count = 0
            
            for user in users:
                telegram_id = user['user_id']  # это telegram_id в старой структуре
                first_name = user['first_name']
                
                # Получаем internal_id через resolve_user_id
                from db import resolve_user_id
                internal_id = resolve_user_id(telegram_id)
                if not internal_id:
                    print(f"❌ Не удалось найти internal_id для пользователя {first_name} (telegram_id: {telegram_id})")
                    continue
                
                # Проверяем, есть ли уже личный проект
                personal_project_id = get_user_personal_project_id(internal_id)
                
                if personal_project_id:
                    print(f"✅ У пользователя {first_name} (internal_id: {internal_id}) уже есть личный проект (ID: {personal_project_id})")
                    existing_count += 1
                    continue
                
                # Создаем личный проект
                try:
                    cur.execute("""
                        INSERT INTO projects (name, owner_id, color, created_at, active)
                        VALUES ('Личное', %s, '#6366f1', %s, TRUE)
                        RETURNING id;
                    """, (internal_id, datetime.utcnow().isoformat()))
                    
                    project_result = cur.fetchone()
                    personal_project_id = project_result['id']
                    
                    # Добавляем пользователя как участника своего личного проекта
                    cur.execute("""
                        INSERT INTO project_members (project_id, user_id, joined_at)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (project_id, user_id) DO NOTHING;
                    """, (personal_project_id, internal_id, datetime.utcnow().isoformat()))
                    
                    conn.commit()
                    print(f"✅ Создан личный проект для {first_name} (internal_id: {internal_id}) -> проект ID: {personal_project_id}")
                    created_count += 1
                    
                except Exception as e:
                    print(f"❌ Ошибка создания проекта для {first_name} (internal_id: {internal_id}): {e}")
                    conn.rollback()
            
            print(f"\n📊 Результаты миграции:")
            print(f"✅ Создано новых проектов: {created_count}")
            print(f"ℹ️  Уже существовало: {existing_count}")
            print(f"📈 Всего пользователей: {len(users)}")
            
            # Проверяем результат
            cur.execute("""
                SELECT COUNT(*) as total_users,
                       COUNT(p.id) as users_with_personal_projects
                FROM users u
                LEFT JOIN projects p ON u.id = p.owner_id AND p.name = 'Личное' AND p.active = TRUE
            """)
            result = cur.fetchone()
            
            print(f"\n🔍 Проверка:")
            print(f"Всего пользователей: {result['total_users']}")
            print(f"С личными проектами: {result['users_with_personal_projects']}")
            
            if result['total_users'] == result['users_with_personal_projects']:
                print("🎉 Миграция завершена успешно! У всех пользователей есть личные проекты.")
            else:
                print("⚠️  Не у всех пользователей есть личные проекты. Проверьте логи выше.")

if __name__ == "__main__":
    migrate_personal_projects()