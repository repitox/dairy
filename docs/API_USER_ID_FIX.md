# Исправление использования ID пользователей в API

## Проблема
API методы использовали `telegram_id` (внешний ID из Telegram) напрямую в запросах к базе данных, вместо использования внутреннего `id` из таблицы `users`.

## Решение
Добавлена конвертация `telegram_id` → `internal_id` во все GET методы API через функцию `resolve_user_id()`.

## Исправленные методы

### ✅ Shopping API
- `GET /api/shopping` - получение списка покупок
- `GET /api/shopping-lists` - получение списков покупок  
- `GET /api/shopping-lists/{list_id}` - получение конкретного списка
- `DELETE /api/shopping-lists/{list_id}` - удаление списка
- `GET /api/shopping-by-lists` - покупки по спискам

### ✅ Events API
- `GET /api/events` - получение событий пользователя

### ✅ Projects API  
- `GET /api/projects` - получение проектов пользователя
- `GET /api/user-projects` - альтернативный endpoint для проектов
- `DELETE /api/projects/{project_id}` - удаление проекта
- `PUT /api/projects/{project_id}/deactivate` - деактивация проекта
- `GET /api/projects/{project_id}` - получение конкретного проекта
- `GET /api/projects/{project_id}/members` - получение участников проекта

### ✅ Settings API
- `GET /api/user/settings` - получение настроек пользователя
- `GET /api/user/timezone` - получение часового пояса
- `GET /api/settings` - получение настроек dashboard

### ✅ Stats API  
- `GET /api/user-stats` - получение статистики пользователя
- `GET /api/dashboard-counters` - получение счетчиков для навигации

### ✅ Tasks API
- `GET /api/tasks` - получение задач пользователя
- `GET /api/tasks/today` - получение задач на сегодня
- `GET /api/tasks/{task_id}` - получение конкретной задачи

### ✅ Notes API
- `GET /api/notes` - получение заметок пользователя
- `GET /api/notes/{note_id}` - получение конкретной заметки  
- `PUT /api/notes/{note_id}` - обновление заметки
- `DELETE /api/notes/{note_id}` - удаление заметки

## Паттерн исправления

Во все методы добавлен следующий код:
```python
# Конвертируем telegram_id в internal_id
internal_id = resolve_user_id(user_id)
if not internal_id:
    raise HTTPException(status_code=404, detail="User not found")

# Используем internal_id вместо user_id в вызовах БД
result = some_db_function(internal_id, ...)
```

## Результат
Теперь все API методы корректно используют внутренние ID из таблицы `users` для работы с базой данных, что обеспечивает:

- ✅ Корректную работу с миграционной системой БД
- ✅ Правильную изоляцию данных пользователей  
- ✅ Консистентность во всем API
- ✅ Защиту от ошибок при работе с пользователями

## Дата
$(date +%Y-%m-%d)

## Статус  
✅ Завершено - все API методы исправлены