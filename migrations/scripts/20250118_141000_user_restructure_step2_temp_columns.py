"""
Миграция: Добавление временных колонок во все связанные таблицы
Этап 2: Подготовка связанных таблиц
"""

def upgrade(cursor):
    print("🔄 Этап 2: Добавление временных колонок во все связанные таблицы")
    
    # Список таблиц и их колонок для обновления
    tables_to_update = [
        ('events', 'user_id'),
        ('notes', 'user_id'),
        ('project_members', 'user_id'),
        ('projects', 'owner_id'),
        ('purchases', 'user_id'),
        ('reminder_logs', 'user_id'),
        ('shopping', 'user_id'),
        ('shopping_lists', 'user_id'),
        ('tasks', 'user_id'),
        ('user_settings', 'user_id')
    ]
    
    for table_name, column_name in tables_to_update:
        # Добавляем временную колонку, если её ещё нет
        cursor.execute(f"""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = '{table_name}' AND column_name = 'temp_user_id'
                ) THEN
                    ALTER TABLE {table_name} ADD COLUMN temp_user_id INTEGER;
                END IF;
            END $$;
        """)
        
        # Заполняем временную колонку значениями из новых id пользователей
        cursor.execute(f"""
            UPDATE {table_name} 
            SET temp_user_id = u.id
            FROM users u 
            WHERE {table_name}.{column_name} = u.user_id AND {table_name}.temp_user_id IS NULL
        """)
        
        print(f"✅ Обновлена таблица {table_name}")
    
    print("✅ Временные колонки добавлены во все связанные таблицы")

def downgrade(cursor):
    print("🔄 Откат: Удаление временных колонок из всех связанных таблиц")
    
    tables_to_update = [
        'events', 'notes', 'project_members', 'projects', 'purchases',
        'reminder_logs', 'shopping', 'shopping_lists', 'tasks', 'user_settings'
    ]
    
    for table_name in tables_to_update:
        cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN IF EXISTS temp_user_id")
        print(f"✅ Временная колонка удалена из {table_name}")
    
    print("✅ Все временные колонки удалены")

# Совместимость с MigrationManager

def up(cursor):
    return upgrade(cursor)


def down(cursor):
    return downgrade(cursor)