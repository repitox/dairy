# 🚀 Быстрый старт: Миграция реструктуризации пользователей

## 📋 Краткая инструкция

### 1. Подготовка (ОБЯЗАТЕЛЬНО!)

```bash
# Создать резервную копию БД
pg_dump -h localhost -U postgres tg_project > backup_before_migration.sql

# Остановить приложение (или перевести в режим обслуживания)
docker-compose down
```

### 2. Тестирование

```bash
# Запустить контейнеры
docker-compose up -d

# Выполнить тест миграции
docker-compose exec app python migrations/test_migration.py
```

### 3. Выполнение миграции

**Вариант A: Полная автоматическая миграция (рекомендуется)**
```bash
python migrations/run_full_migration.py
```

**Вариант B: Поэтапное выполнение**
```bash
# Шаг 1: Миграция БД
docker-compose exec app python migrations/user_restructure_migration.py

# Шаг 2: Обновление кода
python migrations/update_code_after_migration.py

# Шаг 3: Перезапуск приложения
docker-compose restart app
```

### 4. Проверка результатов

```bash
# Проверить работоспособность
curl http://localhost:8000/health

# Проверить структуру БД
docker-compose exec app python -c "
from db import get_conn
with get_conn() as conn:
    with conn.cursor() as cur:
        cur.execute('SELECT column_name FROM information_schema.columns WHERE table_name = \\'users\\'')
        print([row[0] for row in cur.fetchall()])
"
```

### 5. В случае проблем

```bash
# Автоматический откат
docker-compose exec app python migrations/rollback_migration.py

# Или восстановление из резервной копии
docker-compose down
psql -h localhost -U postgres -d tg_project < backup_before_migration.sql
docker-compose up -d
```

## ⚠️ Важные моменты

- **Время выполнения:** 5-15 минут
- **Простой приложения:** Да, требуется
- **Резервная копия:** Обязательна!
- **Тестирование:** Обязательно перед продакшеном

## 📞 Поддержка

При возникновении проблем:
1. Не паникуйте
2. Сохраните логи ошибок
3. Выполните откат
4. Проанализируйте проблему
5. Исправьте и повторите

## ✅ Чек-лист готовности

- [ ] Резервная копия БД создана
- [ ] Приложение остановлено
- [ ] Пользователи уведомлены о техобслуживании
- [ ] Тестирование выполнено успешно
- [ ] Есть план отката
- [ ] Время для выполнения запланировано

**Готовы? Выполняйте миграцию!** 🚀