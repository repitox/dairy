"""
Добавление настроек по умолчанию для всех пользователей
"""

def up(cursor):
    """Применить миграцию"""
    
    # Получаем всех пользователей без настроек темы
    cursor.execute("""
        SELECT DISTINCT u.telegram_id 
        FROM users u 
        LEFT JOIN user_settings us ON u.telegram_id = us.user_id AND us.key = 'theme'
        WHERE us.user_id IS NULL;
    """)
    users_without_theme = cursor.fetchall()
    
    for user in users_without_theme:
        # user может быть кортежем или словарем в зависимости от курсора
        if hasattr(user, 'keys'):  # RealDictCursor
            user_id = user['telegram_id']
        else:  # обычный курсор
            user_id = user[0]
        
        # Добавляем настройки по умолчанию
        cursor.execute("""
            INSERT INTO user_settings (user_id, key, value) 
            VALUES (%s, 'theme', 'auto')
            ON CONFLICT (user_id, key) DO NOTHING;
        """, (user_id,))
        
        cursor.execute("""
            INSERT INTO user_settings (user_id, key, value) 
            VALUES (%s, 'email_notifications', 'false')
            ON CONFLICT (user_id, key) DO NOTHING;
        """, (user_id,))
        
        cursor.execute("""
            INSERT INTO user_settings (user_id, key, value) 
            VALUES (%s, 'task_reminders', 'true')
            ON CONFLICT (user_id, key) DO NOTHING;
        """, (user_id,))
        
        cursor.execute("""
            INSERT INTO user_settings (user_id, key, value) 
            VALUES (%s, 'timezone', 'Europe/Moscow')
            ON CONFLICT (user_id, key) DO NOTHING;
        """, (user_id,))
    
    if users_without_theme:
        print(f"✅ Добавлены настройки для {len(users_without_theme)} пользователей")
    else:
        print("ℹ️ Все пользователи уже имеют настройки")


def down(cursor):
    """Откатить миграцию"""
    
    # Удаляем настройки по умолчанию (осторожно!)
    cursor.execute("""
        DELETE FROM user_settings 
        WHERE key IN ('theme', 'email_notifications', 'task_reminders', 'timezone')
        AND value IN ('auto', 'false', 'true', 'Europe/Moscow');
    """)
    
    print("✅ Настройки по умолчанию удалены")