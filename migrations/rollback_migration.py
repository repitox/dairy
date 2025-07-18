#!/usr/bin/env python3
"""
Скрипт отката миграции реструктуризации пользователей
⚠️  ВНИМАНИЕ: Этот скрипт восстанавливает старую структуру БД!
"""

import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_conn

def print_rollback_banner():
    """Вывод баннера отката"""
    print("=" * 80)
    print("🔄 ОТКАТ МИГРАЦИИ РЕСТРУКТУРИЗАЦИИ ПОЛЬЗОВАТЕЛЕЙ")
    print("=" * 80)
    print("📅 Дата:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("🎯 Цель: Восстановление старой структуры БД")
    print("⚠️  ВНИМАНИЕ: Это критическая операция!")
    print("=" * 80)

def confirm_rollback():
    """Подтверждение отката"""
    print("\n❓ Причины отката:")
    print("1. Критические ошибки в работе приложения")
    print("2. Потеря данных или нарушение целостности")
    print("3. Проблемы с производительностью")
    print("4. Ошибки в коде приложения")
    
    print("\n📋 Что будет сделано:")
    print("1. Проверка наличия резервных копий")
    print("2. Удаление измененных таблиц")
    print("3. Восстановление из резервных копий")
    print("4. Проверка целостности данных")
    
    response = input("\n❓ Вы уверены, что хотите выполнить откат? Введите 'ROLLBACK' для подтверждения: ")
    return response == 'ROLLBACK'

def check_backup_tables():
    """Проверка наличия резервных таблиц"""
    print("🔍 Проверка наличия резервных таблиц...")
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Проверяем схему backup
                cur.execute("""
                    SELECT COUNT(*) as count
                    FROM information_schema.schemata 
                    WHERE schema_name = 'backup'
                """)
                schema_exists = cur.fetchone()["count"] > 0
                
                if not schema_exists:
                    print("❌ Схема backup не найдена!")
                    return False
                
                # Проверяем резервные таблицы
                cur.execute("""
                    SELECT table_name
                    FROM information_schema.tables 
                    WHERE table_schema = 'backup'
                    AND table_name LIKE '%_backup'
                """)
                backup_tables = cur.fetchall()
                
                if len(backup_tables) == 0:
                    print("❌ Резервные таблицы не найдены!")
                    return False
                
                print(f"✅ Найдено {len(backup_tables)} резервных таблиц:")
                for table in backup_tables:
                    print(f"   - {table['table_name']}")
                
                return True
                
    except Exception as e:
        print(f"❌ Ошибка проверки резервных таблиц: {e}")
        return False

def rollback_tables():
    """Откат таблиц к резервным копиям"""
    print("🔄 Восстановление таблиц из резервных копий...")
    
    # Список таблиц для восстановления
    tables = [
        'users', 'events', 'notes', 'project_members', 'projects',
        'purchases', 'reminder_logs', 'shopping', 'shopping_lists',
        'tasks', 'user_settings'
    ]
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                for table in tables:
                    print(f"🔄 Восстановление таблицы {table}...")
                    
                    # Проверяем наличие резервной копии
                    cur.execute("""
                        SELECT COUNT(*) as count
                        FROM information_schema.tables 
                        WHERE table_schema = 'backup'
                        AND table_name = %s
                    """, (f"{table}_backup",))
                    
                    if cur.fetchone()["count"] == 0:
                        print(f"⚠️  Резервная копия {table}_backup не найдена, пропускаем...")
                        continue
                    
                    # Удаляем текущую таблицу
                    cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                    
                    # Восстанавливаем из резервной копии
                    cur.execute(f"""
                        CREATE TABLE {table} AS 
                        SELECT * FROM backup.{table}_backup
                    """)
                    
                    # Восстанавливаем первичные ключи и индексы для users
                    if table == 'users':
                        cur.execute("""
                            ALTER TABLE users 
                            ADD CONSTRAINT users_pkey PRIMARY KEY (user_id)
                        """)
                    
                    print(f"✅ Таблица {table} восстановлена")
                
                conn.commit()
                print("✅ Все таблицы восстановлены из резервных копий")
                return True
                
    except Exception as e:
        print(f"❌ Ошибка восстановления таблиц: {e}")
        return False

def verify_rollback():
    """Проверка успешности отката"""
    print("🔍 Проверка результатов отката...")
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Проверяем структуру users
                cur.execute("""
                    SELECT column_name, data_type
                    FROM information_schema.columns 
                    WHERE table_name = 'users'
                    ORDER BY ordinal_position
                """)
                columns = cur.fetchall()
                
                print("📊 Структура таблицы users после отката:")
                for col in columns:
                    print(f"   - {col['column_name']} ({col['data_type']})")
                
                # Проверяем наличие user_id как первичного ключа
                column_names = [col['column_name'] for col in columns]
                if "user_id" in column_names and "id" not in column_names:
                    print("✅ Структура users восстановлена корректно")
                else:
                    print("❌ Структура users восстановлена некорректно")
                    return False
                
                # Проверяем данные
                cur.execute("SELECT COUNT(*) as count FROM users")
                users_count = cur.fetchone()["count"]
                
                cur.execute("SELECT COUNT(*) as count FROM tasks")
                tasks_count = cur.fetchone()["count"]
                
                # Проверяем связи
                cur.execute("""
                    SELECT COUNT(*) as count
                    FROM tasks t
                    JOIN users u ON t.user_id = u.user_id
                """)
                linked_tasks = cur.fetchone()["count"]
                
                print(f"📈 Статистика после отката:")
                print(f"   - Пользователей: {users_count}")
                print(f"   - Задач: {tasks_count}")
                print(f"   - Задач со связанными пользователями: {linked_tasks}")
                
                if linked_tasks == tasks_count:
                    print("✅ Связи между таблицами восстановлены корректно")
                else:
                    print("⚠️  Возможны проблемы со связями между таблицами")
                
                return True
                
    except Exception as e:
        print(f"❌ Ошибка проверки отката: {e}")
        return False

def cleanup_backup_schema():
    """Очистка схемы backup после успешного отката"""
    response = input("\n❓ Удалить резервные таблицы? (y/n): ")
    if response.lower() != 'y':
        print("ℹ️  Резервные таблицы сохранены")
        return
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS backup CASCADE")
                conn.commit()
                print("✅ Резервные таблицы удалены")
    except Exception as e:
        print(f"❌ Ошибка удаления резервных таблиц: {e}")

def restore_code():
    """Восстановление старого кода"""
    print("🔄 Восстановление кода приложения...")
    
    backup_file = "/Users/d.dubenetskiy/Documents/tg_project/db.py.backup"
    main_file = "/Users/d.dubenetskiy/Documents/tg_project/db.py"
    
    try:
        if os.path.exists(backup_file):
            # Создаем копию текущего файла
            os.rename(main_file, f"{main_file}.after_migration")
            
            # Восстанавливаем из резервной копии
            os.rename(backup_file, main_file)
            
            print("✅ Код приложения восстановлен из резервной копии")
            print(f"ℹ️  Текущий код сохранен как db.py.after_migration")
        else:
            print("⚠️  Резервная копия кода не найдена")
            print("🔍 Проверьте код вручную")
    except Exception as e:
        print(f"❌ Ошибка восстановления кода: {e}")

def main():
    """Главная функция отката"""
    print_rollback_banner()
    
    if not confirm_rollback():
        print("❌ Откат отменен пользователем")
        return
    
    print("\n🚀 Начинаем откат миграции...")
    
    # Проверка резервных копий
    if not check_backup_tables():
        print("❌ Откат невозможен - нет резервных копий")
        return
    
    # Восстановление таблиц
    if not rollback_tables():
        print("❌ Ошибка восстановления таблиц")
        return
    
    # Проверка результатов
    if not verify_rollback():
        print("❌ Проверка отката не пройдена")
        return
    
    # Восстановление кода
    restore_code()
    
    print("\n" + "=" * 80)
    print("✅ ОТКАТ МИГРАЦИИ ЗАВЕРШЕН УСПЕШНО!")
    print("=" * 80)
    
    print("\n📋 Следующие шаги:")
    print("1. ✅ Перезапустите приложение")
    print("2. ✅ Проверьте работоспособность всех функций")
    print("3. ✅ Уведомите пользователей о восстановлении работы")
    print("4. ✅ Проанализируйте причины отката")
    print("5. ✅ Подготовьте план исправления проблем")
    
    # Очистка резервных таблиц
    cleanup_backup_schema()
    
    print("\n🎯 Старая структура БД восстановлена!")

if __name__ == "__main__":
    main()