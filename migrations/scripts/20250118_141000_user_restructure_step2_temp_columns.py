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
    
    # Определяем, какое поле есть в users для связи
    cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='user_id')")
    user_id_exists = bool(cursor.fetchone()[0])
    cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='telegram_id')")
    telegram_id_exists = bool(cursor.fetchone()[0])
    join_field = 'user_id' if user_id_exists else ('telegram_id' if telegram_id_exists else None)

    for table_name, column_name in tables_to_update:
        # Добавляем временную колонку, если её ещё нет
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS temp_user_id INTEGER")

        # Проверяем, есть ли колонка для связи в таблице (возможен частично применённый прод)
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name=%s AND column_name=%s)",
            (table_name, column_name),
        )
        has_link_col = bool(cursor.fetchone()[0])

        if join_field and has_link_col:
            # Заполняем temp_user_id
            cursor.execute(
                f"""
                UPDATE {table_name} t
                SET temp_user_id = u.id
                FROM users u
                WHERE t.{column_name} = u.{join_field} AND t.temp_user_id IS NULL
                """
            )
        
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