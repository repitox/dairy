#!/usr/bin/env python3
"""
Полная миграция структуры БД к новому формату
"""

from db import get_conn
from datetime import datetime

def complete_db_migration():
    """
    Завершает миграцию БД к новой структуре:
    1. Добавляет поля id, telegram_id в users
    2. Переносит данные
    3. Обновляет связи в других таблицах
    4. Создает личные проекты
    """
    print("🔄 Начинаем полную миграцию БД...")
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            try:
                # 1. Проверяем текущую структуру users
                cur.execute("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = 'id'
                """)
                has_id_column = cur.fetchone()
                
                if not has_id_column:
                    print("📝 Добавляем поле id в таблицу users...")
                    
                    # Добавляем новые поля
                    cur.execute("ALTER TABLE users ADD COLUMN id SERIAL PRIMARY KEY")
                    cur.execute("ALTER TABLE users ADD COLUMN telegram_id BIGINT")
                    
                    # Копируем данные из user_id в telegram_id
                    cur.execute("UPDATE users SET telegram_id = user_id")
                    
                    # Добавляем уникальный индекс
                    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS users_telegram_id_unique ON users(telegram_id)")
                    
                    conn.commit()
                    print("✅ Структура users обновлена")
                else:
                    print("✅ Таблица users уже имеет новую структуру")
                
                # 2. Проверяем и обновляем связи в других таблицах
                print("📝 Обновляем связи в других таблицах...")
                
                # Получаем маппинг telegram_id -> internal_id
                cur.execute("SELECT telegram_id, id FROM users")
                user_mapping = {row['telegram_id']: row['id'] for row in cur.fetchall()}
                print(f"📊 Найдено пользователей для обновления: {len(user_mapping)}")
                
                # Обновляем projects.owner_id (если еще не обновлено)
                cur.execute("SELECT id, owner_id FROM projects WHERE owner_id > 1000000")  # telegram_id обычно большие числа
                projects_to_update = cur.fetchall()
                
                for project in projects_to_update:
                    old_owner_id = project['owner_id']
                    if old_owner_id in user_mapping:
                        new_owner_id = user_mapping[old_owner_id]
                        cur.execute("UPDATE projects SET owner_id = %s WHERE id = %s", 
                                  (new_owner_id, project['id']))
                        print(f"  📁 Проект {project['id']}: owner_id {old_owner_id} -> {new_owner_id}")
                
                # Обновляем tasks.user_id
                cur.execute("SELECT id, user_id FROM tasks WHERE user_id > 1000000")
                tasks_to_update = cur.fetchall()
                
                for task in tasks_to_update:
                    old_user_id = task['user_id']
                    if old_user_id in user_mapping:
                        new_user_id = user_mapping[old_user_id]
                        cur.execute("UPDATE tasks SET user_id = %s WHERE id = %s", 
                                  (new_user_id, task['id']))
                        print(f"  📋 Задача {task['id']}: user_id {old_user_id} -> {new_user_id}")
                
                # Обновляем events.user_id
                cur.execute("SELECT id, user_id FROM events WHERE user_id > 1000000")
                events_to_update = cur.fetchall()
                
                for event in events_to_update:
                    old_user_id = event['user_id']
                    if old_user_id in user_mapping:
                        new_user_id = user_mapping[old_user_id]
                        cur.execute("UPDATE events SET user_id = %s WHERE id = %s", 
                                  (new_user_id, event['id']))
                        print(f"  📅 Событие {event['id']}: user_id {old_user_id} -> {new_user_id}")
                
                # Обновляем другие таблицы аналогично...
                tables_to_update = [
                    'shopping', 'purchases', 'shopping_lists', 'notes', 
                    'user_settings', 'project_members'
                ]
                
                for table in tables_to_update:
                    try:
                        cur.execute(f"SELECT id, user_id FROM {table} WHERE user_id > 1000000 LIMIT 5")
                        records = cur.fetchall()
                        
                        if records:
                            for record in records:
                                old_user_id = record['user_id']
                                if old_user_id in user_mapping:
                                    new_user_id = user_mapping[old_user_id]
                                    cur.execute(f"UPDATE {table} SET user_id = %s WHERE id = %s", 
                                              (new_user_id, record['id']))
                            print(f"  📊 Обновлена таблица {table}: {len(records)} записей")
                    except Exception as e:
                        print(f"  ⚠️  Таблица {table}: {e}")
                
                conn.commit()
                print("✅ Связи обновлены")
                
                # 3. Создаем личные проекты для всех пользователей
                print("📝 Создаем личные проекты...")
                
                cur.execute("SELECT id, telegram_id, first_name FROM users")
                users = cur.fetchall()
                
                created_count = 0
                existing_count = 0
                
                for user in users:
                    internal_id = user['id']
                    telegram_id = user['telegram_id']
                    first_name = user['first_name']
                    
                    # Проверяем, есть ли личный проект
                    cur.execute("""
                        SELECT id FROM projects 
                        WHERE owner_id = %s AND name = 'Личное' AND active = TRUE
                    """, (internal_id,))
                    
                    if cur.fetchone():
                        existing_count += 1
                        continue
                    
                    # Создаем личный проект
                    cur.execute("""
                        INSERT INTO projects (name, owner_id, color, created_at, active)
                        VALUES ('Личное', %s, '#6366f1', %s, TRUE)
                        RETURNING id;
                    """, (internal_id, datetime.utcnow().isoformat()))
                    
                    project_result = cur.fetchone()
                    personal_project_id = project_result['id']
                    
                    # Добавляем в project_members
                    cur.execute("""
                        INSERT INTO project_members (project_id, user_id, joined_at)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (project_id, user_id) DO NOTHING;
                    """, (personal_project_id, internal_id, datetime.utcnow().isoformat()))
                    
                    print(f"  ✅ Создан личный проект для {first_name} (ID: {internal_id})")
                    created_count += 1
                
                conn.commit()
                
                print(f"\n🎉 Миграция завершена успешно!")
                print(f"📊 Личных проектов создано: {created_count}")
                print(f"📊 Уже существовало: {existing_count}")
                print(f"📊 Всего пользователей: {len(users)}")
                
            except Exception as e:
                print(f"❌ Ошибка миграции: {e}")
                conn.rollback()
                raise

if __name__ == "__main__":
    complete_db_migration()#!/usr/bin/env python3
"""
Полная миграция структуры БД к новому формату
"""

from db import get_conn
from datetime import datetime

def complete_db_migration():
    """
    Завершает миграцию БД к новой структуре:
    1. Добавляет поля id, telegram_id в users
    2. Переносит данные
    3. Обновляет связи в других таблицах
    4. Создает личные проекты
    """
    print("🔄 Начинаем полную миграцию БД...")
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            try:
                # 1. Проверяем текущую структуру users
                cur.execute("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = 'id'
                """)
                has_id_column = cur.fetchone()
                
                if not has_id_column:
                    print("📝 Добавляем поле id в таблицу users...")
                    
                    # Добавляем новые поля
                    cur.execute("ALTER TABLE users ADD COLUMN id SERIAL PRIMARY KEY")
                    cur.execute("ALTER TABLE users ADD COLUMN telegram_id BIGINT")
                    
                    # Копируем данные из user_id в telegram_id
                    cur.execute("UPDATE users SET telegram_id = user_id")
                    
                    # Добавляем уникальный индекс
                    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS users_telegram_id_unique ON users(telegram_id)")
                    
                    conn.commit()
                    print("✅ Структура users обновлена")
                else:
                    print("✅ Таблица users уже имеет новую структуру")
                
                # 2. Проверяем и обновляем связи в других таблицах
                print("📝 Обновляем связи в других таблицах...")
                
                # Получаем маппинг telegram_id -> internal_id
                cur.execute("SELECT telegram_id, id FROM users")
                user_mapping = {row['telegram_id']: row['id'] for row in cur.fetchall()}
                print(f"📊 Найдено пользователей для обновления: {len(user_mapping)}")
                
                # Обновляем projects.owner_id (если еще не обновлено)
                cur.execute("SELECT id, owner_id FROM projects WHERE owner_id > 1000000")  # telegram_id обычно большие числа
                projects_to_update = cur.fetchall()
                
                for project in projects_to_update:
                    old_owner_id = project['owner_id']
                    if old_owner_id in user_mapping:
                        new_owner_id = user_mapping[old_owner_id]
                        cur.execute("UPDATE projects SET owner_id = %s WHERE id = %s", 
                                  (new_owner_id, project['id']))
                        print(f"  📁 Проект {project['id']}: owner_id {old_owner_id} -> {new_owner_id}")
                
                # Обновляем tasks.user_id
                cur.execute("SELECT id, user_id FROM tasks WHERE user_id > 1000000")
                tasks_to_update = cur.fetchall()
                
                for task in tasks_to_update:
                    old_user_id = task['user_id']
                    if old_user_id in user_mapping:
                        new_user_id = user_mapping[old_user_id]
                        cur.execute("UPDATE tasks SET user_id = %s WHERE id = %s", 
                                  (new_user_id, task['id']))
                        print(f"  📋 Задача {task['id']}: user_id {old_user_id} -> {new_user_id}")
                
                # Обновляем events.user_id
                cur.execute("SELECT id, user_id FROM events WHERE user_id > 1000000")
                events_to_update = cur.fetchall()
                
                for event in events_to_update:
                    old_user_id = event['user_id']
                    if old_user_id in user_mapping:
                        new_user_id = user_mapping[old_user_id]
                        cur.execute("UPDATE events SET user_id = %s WHERE id = %s", 
                                  (new_user_id, event['id']))
                        print(f"  📅 Событие {event['id']}: user_id {old_user_id} -> {new_user_id}")
                
                # Обновляем другие таблицы аналогично...
                tables_to_update = [
                    'shopping', 'purchases', 'shopping_lists', 'notes', 
                    'user_settings', 'project_members'
                ]
                
                for table in tables_to_update:
                    try:
                        cur.execute(f"SELECT id, user_id FROM {table} WHERE user_id > 1000000 LIMIT 5")
                        records = cur.fetchall()
                        
                        if records:
                            for record in records:
                                old_user_id = record['user_id']
                                if old_user_id in user_mapping:
                                    new_user_id = user_mapping[old_user_id]
                                    cur.execute(f"UPDATE {table} SET user_id = %s WHERE id = %s", 
                                              (new_user_id, record['id']))
                            print(f"  📊 Обновлена таблица {table}: {len(records)} записей")
                    except Exception as e:
                        print(f"  ⚠️  Таблица {table}: {e}")
                
                conn.commit()
                print("✅ Связи обновлены")
                
                # 3. Создаем личные проекты для всех пользователей
                print("📝 Создаем личные проекты...")
                
                cur.execute("SELECT id, telegram_id, first_name FROM users")
                users = cur.fetchall()
                
                created_count = 0
                existing_count = 0
                
                for user in users:
                    internal_id = user['id']
                    telegram_id = user['telegram_id']
                    first_name = user['first_name']
                    
                    # Проверяем, есть ли личный проект
                    cur.execute("""
                        SELECT id FROM projects 
                        WHERE owner_id = %s AND name = 'Личное' AND active = TRUE
                    """, (internal_id,))
                    
                    if cur.fetchone():
                        existing_count += 1
                        continue
                    
                    # Создаем личный проект
                    cur.execute("""
                        INSERT INTO projects (name, owner_id, color, created_at, active)
                        VALUES ('Личное', %s, '#6366f1', %s, TRUE)
                        RETURNING id;
                    """, (internal_id, datetime.utcnow().isoformat()))
                    
                    project_result = cur.fetchone()
                    personal_project_id = project_result['id']
                    
                    # Добавляем в project_members
                    cur.execute("""
                        INSERT INTO project_members (project_id, user_id, joined_at)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (project_id, user_id) DO NOTHING;
                    """, (personal_project_id, internal_id, datetime.utcnow().isoformat()))
                    
                    print(f"  ✅ Создан личный проект для {first_name} (ID: {internal_id})")
                    created_count += 1
                
                conn.commit()
                
                print(f"\n🎉 Миграция завершена успешно!")
                print(f"📊 Личных проектов создано: {created_count}")
                print(f"📊 Уже существовало: {existing_count}")
                print(f"📊 Всего пользователей: {len(users)}")
                
            except Exception as e:
                print(f"❌ Ошибка миграции: {e}")
                conn.rollback()
                raise

if __name__ == "__main__":
    complete_db_migration()