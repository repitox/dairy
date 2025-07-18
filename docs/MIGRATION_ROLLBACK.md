# 🔄 Откат миграции реструктуризации пользователей

## ⚠️ Когда нужен откат

Откат миграции может потребоваться в следующих случаях:
- Обнаружены критические ошибки в работе приложения
- Потеря данных или нарушение целостности
- Неожиданные проблемы с производительностью
- Ошибки в коде приложения после миграции

## 🚨 Экстренный откат (быстрый)

### Вариант 1: Восстановление из резервной копии БД

```bash
# 1. Остановить приложение
docker-compose down

# 2. Восстановить БД из резервной копии
# (команда зависит от способа создания резервной копии)
psql -h localhost -U postgres -d tg_project < backup_before_migration.sql

# 3. Восстановить старый код
cp db.py.backup db.py

# 4. Запустить приложение
docker-compose up -d
```

### Вариант 2: Использование резервных таблиц

```sql
-- Подключиться к БД
psql -h localhost -U postgres -d tg_project

-- Восстановить таблицы из резервных копий
BEGIN;

-- Удалить измененные таблицы
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS notes CASCADE;
DROP TABLE IF EXISTS project_members CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS purchases CASCADE;
DROP TABLE IF EXISTS reminder_logs CASCADE;
DROP TABLE IF EXISTS shopping CASCADE;
DROP TABLE IF EXISTS shopping_lists CASCADE;
DROP TABLE IF EXISTS tasks CASCADE;
DROP TABLE IF EXISTS user_settings CASCADE;

-- Восстановить из резервных копий
ALTER TABLE backup.users_backup RENAME TO users;
ALTER TABLE backup.events_backup RENAME TO events;
ALTER TABLE backup.notes_backup RENAME TO notes;
ALTER TABLE backup.project_members_backup RENAME TO project_members;
ALTER TABLE backup.projects_backup RENAME TO projects;
ALTER TABLE backup.purchases_backup RENAME TO purchases;
ALTER TABLE backup.reminder_logs_backup RENAME TO reminder_logs;
ALTER TABLE backup.shopping_backup RENAME TO shopping;
ALTER TABLE backup.shopping_lists_backup RENAME TO shopping_lists;
ALTER TABLE backup.tasks_backup RENAME TO tasks;
ALTER TABLE backup.user_settings_backup RENAME TO user_settings;

-- Переместить таблицы из схемы backup в public
ALTER TABLE backup.users SET SCHEMA public;
ALTER TABLE backup.events SET SCHEMA public;
ALTER TABLE backup.notes SET SCHEMA public;
ALTER TABLE backup.project_members SET SCHEMA public;
ALTER TABLE backup.projects SET SCHEMA public;
ALTER TABLE backup.purchases SET SCHEMA public;
ALTER TABLE backup.reminder_logs SET SCHEMA public;
ALTER TABLE backup.shopping SET SCHEMA public;
ALTER TABLE backup.shopping_lists SET SCHEMA public;
ALTER TABLE backup.tasks SET SCHEMA public;
ALTER TABLE backup.user_settings SET SCHEMA public;

COMMIT;
```

## 🔧 Поэтапный откат

### Этап 1: Остановка приложения

```bash
# Остановить приложение
docker-compose down

# Или перевести в режим обслуживания
# (если есть такая возможность)
```

### Этап 2: Проверка состояния БД

```sql
-- Проверить, какие изменения были сделаны
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY ordinal_position;

-- Проверить наличие резервных таблиц
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'backup';
```

### Этап 3: Восстановление данных

```python
# Скрипт для автоматического отката
# migrations/rollback_migration.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_conn

def rollback_migration():
    """Автоматический откат миграции"""
    print("🔄 Начинаем откат миграции...")
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Проверяем наличие резервных таблиц
                cur.execute("""
                    SELECT COUNT(*) as count
                    FROM information_schema.tables 
                    WHERE table_schema = 'backup'
                """)
                backup_count = cur.fetchone()["count"]
                
                if backup_count == 0:
                    print("❌ Резервные таблицы не найдены!")
                    return False
                
                print(f"✅ Найдено {backup_count} резервных таблиц")
                
                # Список таблиц для восстановления
                tables = [
                    'users', 'events', 'notes', 'project_members', 'projects',
                    'purchases', 'reminder_logs', 'shopping', 'shopping_lists',
                    'tasks', 'user_settings'
                ]
                
                # Восстанавливаем каждую таблицу
                for table in tables:
                    print(f"🔄 Восстановление таблицы {table}...")
                    
                    # Удаляем текущую таблицу
                    cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                    
                    # Восстанавливаем из резервной копии
                    cur.execute(f"""
                        CREATE TABLE {table} AS 
                        SELECT * FROM backup.{table}_backup
                    """)
                    
                    print(f"✅ Таблица {table} восстановлена")
                
                conn.commit()
                print("✅ Откат миграции завершен успешно!")
                return True
                
    except Exception as e:
        print(f"❌ Ошибка отката: {e}")
        return False

if __name__ == "__main__":
    rollback_migration()
```

### Этап 4: Восстановление кода

```bash
# Восстановить старый код из резервной копии
cp db.py.backup db.py

# Удалить новые функции (если они были добавлены)
# Проверить и исправить вручную
```

### Этап 5: Проверка после отката

```python
# Скрипт проверки после отката
def verify_rollback():
    """Проверка успешности отката"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Проверяем структуру users
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users'
            """)
            columns = [row["column_name"] for row in cur.fetchall()]
            
            if "user_id" in columns and "id" not in columns:
                print("✅ Структура users восстановлена")
            else:
                print("❌ Структура users не восстановлена")
            
            # Проверяем данные
            cur.execute("SELECT COUNT(*) as count FROM users")
            users_count = cur.fetchone()["count"]
            
            cur.execute("SELECT COUNT(*) as count FROM tasks")
            tasks_count = cur.fetchone()["count"]
            
            print(f"📊 Данные после отката:")
            print(f"   - Пользователей: {users_count}")
            print(f"   - Задач: {tasks_count}")
```

## 📋 Чек-лист после отката

- [ ] Приложение запускается без ошибок
- [ ] Пользователи могут войти в систему
- [ ] Все основные функции работают
- [ ] Данные не потеряны
- [ ] Производительность в норме
- [ ] Логи не содержат критических ошибок

## 🔍 Анализ причин отката

После успешного отката важно проанализировать причины:

1. **Технические проблемы:**
   - Ошибки в миграционных скриптах
   - Проблемы с обновлением кода
   - Неожиданные конфликты данных

2. **Проблемы планирования:**
   - Недостаточное тестирование
   - Неучтенные зависимости
   - Неправильная оценка времени

3. **Рекомендации для повторной попытки:**
   - Дополнительное тестирование
   - Исправление найденных ошибок
   - Улучшение процедур миграции

## 📞 Контакты для экстренных случаев

В случае критических проблем:
1. Немедленно остановить приложение
2. Уведомить пользователей о проблемах
3. Начать процедуру отката
4. Документировать все действия
5. Анализировать причины после восстановления

## 🎯 Заключение

Откат миграции - это крайняя мера, но иногда необходимая. Главное:
- Действовать быстро и решительно
- Использовать заранее подготовленные процедуры
- Документировать все действия
- Анализировать причины для предотвращения повторения