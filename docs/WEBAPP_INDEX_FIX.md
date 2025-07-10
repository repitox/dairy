# Исправление главной страницы WebApp

## Проблема
На главной странице WebApp (`/static/index.html`) вместо данных о задачах, событиях и покупках отображалась "Ошибка загрузки".

## Причины проблем

### 1. Конфликт роутов FastAPI
**Проблема**: Роут `/api/tasks/today` был определен после `/api/tasks/{task_id}`, из-за чего FastAPI пытался парсить "today" как task_id.

**Решение**: Переместили специфичные роуты (`/api/tasks/today`) выше параметризованных (`/api/tasks/{task_id}`).

### 2. Сложная логика часовых поясов
**Проблема**: Функции `get_today_tasks()` и `get_today_events()` использовали сложную логику с `datetime_utils`, которая работала нестабильно.

**Решение**: Упростили логику до простого сравнения дат без учета часовых поясов для `/today` эндпоинтов.

### 3. Отсутствие связи пользователя с проектами
**Проблема**: Тестовый пользователь (123456789) не был участником проектов, поэтому не видел задачи и события.

**Решение**: Добавили отладочный эндпоинт `/api/debug/add-user-to-project` и добавили пользователя в проект.

## Внесенные изменения

### bot.py
```python
# Перемещен роут /api/tasks/today выше /api/tasks/{task_id}
@app.get("/api/tasks/today")
async def api_today_tasks(user_id: int):
    result = get_today_tasks(user_id)
    return {
        "overdue": result.get("overdue", []),
        "today": result.get("today", [])
    }

# Добавлен отладочный эндпоинт
@app.post("/api/debug/add-user-to-project")
async def debug_add_user_to_project(request: Request):
    # ...
```

### db.py
```python
def get_today_tasks(user_id: int):
    """Упрощенная логика без сложных часовых поясов"""
    from datetime import datetime, date
    
    # Простое сравнение дат
    today = date.today()
    # ...

def get_today_events(user_id: int):
    """Упрощенная логика для событий"""
    from datetime import datetime, date
    
    # Простое сравнение дат
    today = date.today()
    # ...
```

### static/index.html
```javascript
// Улучшена обработка ошибок с детальным логированием
try {
    taskRes = await fetch(`/api/tasks/today?user_id=${userId}`);
    console.log("Ответ задач:", taskRes.status, taskRes.statusText);
} catch (error) {
    console.error("Ошибка запроса задач:", error);
    taskRes = { ok: false, status: 0, statusText: error.message };
}
```

## Результат

✅ **Задачи**: Отображаются корректно с группировкой "Просроченные" и "На сегодня"
✅ **События**: Показываются события на текущий день
✅ **Покупки**: API работает (пустой список для тестового пользователя)
✅ **Обработка ошибок**: Улучшено логирование для отладки

## Тестирование

```bash
# Проверка API
curl "http://localhost:8000/api/tasks/today?user_id=123456789"
curl "http://localhost:8000/api/events/today?user_id=123456789"
curl "http://localhost:8000/api/shopping/today?user_id=123456789"

# Добавление пользователя в проект (если нужно)
curl -X POST "http://localhost:8000/api/debug/add-user-to-project" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123456789, "project_id": 3}'
```

## Открыть WebApp
http://localhost:8000/webapp/