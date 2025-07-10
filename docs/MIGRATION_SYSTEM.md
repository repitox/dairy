# 🔄 Система миграций базы данных

Универсальная система для управления миграциями между локальной разработкой (Docker) и продакшн сервером (NetAngels).

## 📁 Структура

```
migrations/
├── __init__.py
├── migration_manager.py    # Основной менеджер миграций
└── scripts/               # Скрипты миграций
    ├── __init__.py
    ├── 20241220_120000_initial_schema.py
    ├── 20241220_120001_add_extended_fields.py
    ├── 20241220_120002_create_purchases_table.py
    └── 20241220_120003_default_user_settings.py

deploy_sync.py             # Скрипт для синхронизации локал <-> продакшн
server_migrate.py          # Автономный скрипт для сервера
```

## 🚀 Использование

### Локальная разработка

```bash
# Проверить статус миграций (локал и продакшн)
python deploy_sync.py status

# Синхронизировать локальную БД с продакшн
python deploy_sync.py sync

# Создать новую миграцию
python deploy_sync.py create --name add_new_field

# Создать дампы схем для сравнения
python deploy_sync.py dump
```

### На сервере NetAngels

1. Загрузите файл `server_migrate.py` на сервер
2. Выполните миграции:

```bash
# Проверить статус
python3 server_migrate.py status

# Выполнить все миграции
python3 server_migrate.py migrate
```

## 📝 Создание новых миграций

### 1. Создание шаблона

```bash
python deploy_sync.py create --name add_user_avatar
```

Это создаст файл `migrations/scripts/YYYYMMDD_HHMMSS_add_user_avatar.py`

### 2. Редактирование миграции

```python
"""
Добавление аватара пользователя
"""

def up(cursor):
    """Применить миграцию"""
    
    cursor.execute("""
        ALTER TABLE users 
        ADD COLUMN avatar_url TEXT;
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_avatar 
        ON users(avatar_url);
    """)
    
    print("✅ Добавлено поле avatar_url")


def down(cursor):
    """Откатить миграцию"""
    
    cursor.execute("DROP INDEX IF EXISTS idx_users_avatar;")
    cursor.execute("ALTER TABLE users DROP COLUMN IF EXISTS avatar_url;")
    
    print("✅ Поле avatar_url удалено")
```

### 3. Применение миграции

```bash
# Локально
python deploy_sync.py sync

# На сервере
python3 server_migrate.py migrate
```

## 🔧 Настройки подключения

### Локальная БД (Docker)
```
postgresql://postgres:password@localhost:5432/telegram_app
```

### Продакшн БД (NetAngels)
```
Host: postgres.c107597.h2
Database: c107597_rptx_na4u_ru
User: c107597_rptx_na4u_ru
Password: ZiKceXoydixol93
Port: 5432
```

## 📊 Отслеживание миграций

Система создаёт таблицу `schema_migrations` для отслеживания выполненных миграций:

```sql
CREATE TABLE schema_migrations (
    id SERIAL PRIMARY KEY,
    version VARCHAR(255) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    checksum TEXT
);
```

## 🛡️ Безопасность

- Все миграции выполняются в транзакциях
- При ошибке происходит автоматический откат
- Каждая миграция выполняется только один раз
- Ведётся лог всех выполненных миграций

## 📋 Существующие миграции

1. **20241220_120000_initial_schema** - Создание базовой схемы БД
2. **20241220_120001_add_extended_fields** - Добавление расширенных полей и индексов
3. **20241220_120002_create_purchases_table** - Создание таблицы purchases
4. **20241220_120003_default_user_settings** - Настройки пользователей по умолчанию

## 🔄 Процесс деплоя

1. Разработка локально с Docker
2. Создание миграций при необходимости
3. Тестирование миграций локально
4. Загрузка `server_migrate.py` на сервер
5. Выполнение миграций на продакшн
6. Проверка работоспособности

## 🆘 Устранение проблем

### Ошибка подключения к БД
```bash
# Проверьте настройки подключения
python deploy_sync.py status
```

### Миграция не выполняется
```bash
# Проверьте синтаксис в файле миграции
# Убедитесь, что функции up() и down() определены
```

### Откат миграции
```python
# В migration_manager.py есть метод rollback_migration()
# Используйте осторожно на продакшн!
```

## 📈 Расширение системы

Система легко расширяется:

- Добавьте новые миграции в `migrations/scripts/`
- Используйте формат имени: `YYYYMMDD_HHMMSS_description.py`
- Обязательно реализуйте функции `up()` и `down()`
- Тестируйте локально перед деплоем

## 🎯 Лучшие практики

1. **Именование**: Используйте описательные имена миграций
2. **Атомарность**: Одна миграция = одно логическое изменение
3. **Обратимость**: Всегда реализуйте функцию `down()`
4. **Тестирование**: Проверяйте миграции локально
5. **Бэкапы**: Делайте резервные копии перед миграциями на продакшн