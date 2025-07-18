# 🔄 Система миграций - Реструктуризация пользователей

## 📁 Структура файлов

### 🎯 Главные скрипты
- **`run_full_migration.py`** - Полная автоматическая миграция (РЕКОМЕНДУЕТСЯ)
- **`user_restructure_migration.py`** - Основной скрипт миграции БД
- **`rollback_migration.py`** - Автоматический откат миграции
- **`update_code_after_migration.py`** - Обновление кода приложения
- **`test_migration.py`** - Тестирование перед миграцией

### 📂 Поэтапные миграции (`scripts/`)
1. **`20250118_140000_user_restructure_step1_add_id.py`** - Добавление поля `id`
2. **`20250118_141000_user_restructure_step2_temp_columns.py`** - Временные колонки
3. **`20250118_142000_user_restructure_step3_switch_columns.py`** - Переключение колонок
4. **`20250118_143000_user_restructure_step4_finalize.py`** - Финализация и внешние ключи

## 🚀 Быстрый старт

### Полная автоматическая миграция
```bash
python migrations/run_full_migration.py
```

### Поэтапное выполнение
```bash
# 1. Тестирование
python migrations/test_migration.py

# 2. Миграция БД
python migrations/user_restructure_migration.py

# 3. Обновление кода
python migrations/update_code_after_migration.py
```

### Откат в случае проблем
```bash
python migrations/rollback_migration.py
```

## 📊 Что изменяется

### До миграции
```sql
-- Таблица users
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,  -- Telegram ID
    first_name TEXT,
    username TEXT,
    registered_at TEXT,
    theme TEXT
);

-- Связанные таблицы ссылаются на user_id
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id BIGINT,  -- Ссылка на users.user_id
    title TEXT,
    ...
);
```

### После миграции
```sql
-- Таблица users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,       -- Автоинкрементный ID
    telegram_id BIGINT UNIQUE,   -- Telegram ID (бывший user_id)
    first_name TEXT,
    username TEXT,
    registered_at TEXT,
    theme TEXT
);

-- Связанные таблицы ссылаются на id
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,             -- Ссылка на users.id
    title TEXT,
    ...,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## 🔧 Затронутые таблицы

### Основная таблица
- **`users`** - добавление `id`, переименование `user_id` → `telegram_id`

### Связанные таблицы (10 шт.)
- `events` - поле `user_id`
- `notes` - поле `user_id`
- `project_members` - поле `user_id`
- `projects` - поле `owner_id`
- `purchases` - поле `user_id`
- `reminder_logs` - поле `user_id`
- `shopping` - поле `user_id`
- `shopping_lists` - поле `user_id`
- `tasks` - поле `user_id`
- `user_settings` - поле `user_id`

## ⚠️ Важные предупреждения

### Перед миграцией
- ✅ **ОБЯЗАТЕЛЬНО** создайте резервную копию БД
- ✅ Остановите приложение или переведите в режим обслуживания
- ✅ Выполните тестирование на копии данных
- ✅ Уведомите пользователей о техническом обслуживании

### Во время миграции
- ⏱️ Ожидаемое время: 5-15 минут
- 🚫 НЕ прерывайте процесс миграции
- 📝 Сохраняйте все логи
- 🔍 Следите за сообщениями об ошибках

### После миграции
- ✅ Проверьте работоспособность всех функций
- ✅ Выполните чек-лист проверок
- ✅ Мониторьте приложение несколько часов
- ✅ Уведомите пользователей о завершении обслуживания

## 🔄 План отката

В случае проблем:
1. **Немедленно** остановите приложение
2. Выполните автоматический откат: `python migrations/rollback_migration.py`
3. Или восстановите из резервной копии БД
4. Проанализируйте причины проблем
5. Исправьте и повторите миграцию

## 📚 Документация

- **`docs/USER_RESTRUCTURE_PLAN.md`** - Детальный план миграции
- **`docs/MIGRATION_QUICK_START.md`** - Быстрый старт
- **`docs/MIGRATION_ROLLBACK.md`** - Инструкция по откату
- **`docs/POST_MIGRATION_CHECKLIST.md`** - Чек-лист после миграции (создается автоматически)

## 🎯 Преимущества новой структуры

1. **Стандартизация** - классическая структура с автоинкрементным ID
2. **Целостность данных** - внешние ключи для всех связей
3. **Производительность** - оптимизированные индексы
4. **Масштабируемость** - готовность к росту данных
5. **Совместимость** - соответствие стандартам БД

## 🔍 Тестирование

Перед выполнением на продакшене:
```bash
# Тест на копии данных
python migrations/test_migration.py

# Проверка результатов
python -c "
from db import get_conn
with get_conn() as conn:
    with conn.cursor() as cur:
        cur.execute('SELECT COUNT(*) FROM users')
        print(f'Пользователей: {cur.fetchone()[0]}')
        
        cur.execute('SELECT COUNT(*) FROM tasks')
        print(f'Задач: {cur.fetchone()[0]}')
"
```

## 📞 Поддержка

При возникновении проблем:
1. Сохраните полные логи ошибок
2. Выполните откат для восстановления работы
3. Проанализируйте причины
4. Исправьте проблемы
5. Повторите миграцию

---

**Готовы к миграции? Следуйте инструкциям и будьте внимательны!** 🚀