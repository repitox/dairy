#!/usr/bin/env python3
"""
Главный скрипт миграции реструктуризации пользователей
ВНИМАНИЕ: Этот скрипт изменяет структуру БД!
"""

import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_conn

def create_backup():
    """Создание резервной копии всех данных"""
    print("💾 Создание резервной копии всех данных...")
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Создаем схему для резервных копий
                cur.execute("CREATE SCHEMA IF NOT EXISTS backup")
                
                # Список всех таблиц для резервного копирования
                tables = [
                    'users', 'events', 'notes', 'project_members', 'projects',
                    'purchases', 'reminder_logs', 'shopping', 'shopping_lists',
                    'tasks', 'user_settings'
                ]
                
                for table in tables:
                    cur.execute(f"""
                        CREATE TABLE backup.{table}_backup AS 
                        SELECT * FROM {table}
                    """)
                    print(f"✅ Резервная копия создана для {table}")
                
                conn.commit()
                print("✅ Резервная копия всех данных создана")
                return True
                
    except Exception as e:
        print(f"❌ Ошибка создания резервной копии: {e}")
        return False

def run_migration_step(step_number, migration_file):
    """Запуск одного этапа миграции"""
    print(f"\\n🔄 Запуск этапа {step_number}...")
    
    try:
        # Импортируем миграцию
        module_name = migration_file.replace('.py', '')
        module = __import__(f'scripts.{module_name}', fromlist=[''])
        
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Выполняем миграцию
                module.upgrade(cur)
                conn.commit()
                
                print(f"✅ Этап {step_number} завершен успешно")
                return True
                
    except Exception as e:
        print(f"❌ Ошибка на этапе {step_number}: {e}")
        return False

def verify_migration():
    """Проверка результатов миграции"""
    print("\\n🔍 Проверка результатов миграции...")
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Проверяем структуру users
                cur.execute("""
                    SELECT column_name, data_type, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    ORDER BY ordinal_position
                """)
                users_columns = cur.fetchall()
                
                print("📊 Новая структура таблицы users:")
                for col in users_columns:
                    print(f"   - {col['column_name']} ({col['data_type']})")
                
                # Проверяем количество пользователей
                cur.execute("SELECT COUNT(*) as count FROM users")
                users_count = cur.fetchone()["count"]
                
                # Проверяем связи
                cur.execute("""
                    SELECT COUNT(*) as count
                    FROM tasks t
                    JOIN users u ON t.user_id = u.id
                """)
                linked_tasks = cur.fetchone()["count"]
                
                print(f"📈 Статистика после миграции:")
                print(f"   - Пользователей: {users_count}")
                print(f"   - Задач со связанными пользователями: {linked_tasks}")
                
                # Проверяем внешние ключи
                cur.execute("""
                    SELECT 
                        tc.constraint_name,
                        tc.table_name,
                        kcu.column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu 
                        ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND kcu.column_name IN ('user_id', 'owner_id')
                """)
                foreign_keys = cur.fetchall()
                
                print("🔗 Внешние ключи:")
                for fk in foreign_keys:
                    print(f"   - {fk['table_name']}.{fk['column_name']} -> {fk['constraint_name']}")
                
                print("✅ Проверка завершена успешно")
                return True
                
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
        return False

def main():
    """Главная функция миграции"""
    print("🚀 Запуск миграции реструктуризации пользователей")
    print("=" * 60)
    
    # Подтверждение от пользователя
    response = input("⚠️  Это серьезная миграция! Продолжить? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Миграция отменена")
        return
    
    # Создание резервной копии
    if not create_backup():
        print("❌ Миграция прервана из-за ошибки резервного копирования")
        return
    
    # Этапы миграции
    migration_steps = [
        (1, "20250118_140000_user_restructure_step1_add_id.py"),
        (2, "20250118_141000_user_restructure_step2_temp_columns.py"),
        (3, "20250118_142000_user_restructure_step3_switch_columns.py"),
        (4, "20250118_143000_user_restructure_step4_finalize.py")
    ]
    
    # Выполнение всех этапов
    for step_num, migration_file in migration_steps:
        if not run_migration_step(step_num, migration_file):
            print(f"❌ Миграция прервана на этапе {step_num}")
            print("🔄 Используйте резервную копию для восстановления")
            return
    
    # Проверка результатов
    if verify_migration():
        print("\\n🎉 Миграция завершена успешно!")
        print("📋 Новая структура пользователей готова к использованию")
        print("⚠️  Не забудьте обновить код приложения!")
    else:
        print("❌ Проверка миграции не пройдена")
        print("🔄 Рекомендуется использовать резервную копию")

if __name__ == "__main__":
    main()