# Примеры работы с навигацией

**Дата создания**: 7 января 2025  
**Версия**: 1.0  

## Текущее состояние навигации

### 📱 WebApp навигация (отображается в Telegram)

Показывает только страницы **БЕЗ** `/dashboard/` в URL:

```
📂 MAIN:
  🏠 Главная → index.html
  📋 Задачи → tasks.html  
  📅 События → events.html
  🛒 Покупки → shopping.html

📂 PROJECTS:
  📁 Все проекты → project_select.html
  ➕ Создать проект → project_create.html

📂 CREATE:
  📝 Новая задача → task_add.html
  📅 Новое событие → event_create.html
  🛒 Добавить покупку → shopping.html

📂 SETTINGS:
  ⚙️ Настройки → settings.html
  🌍 Часовой пояс → timezone-settings.html
```

### 🖥️ Dashboard навигация (отображается в браузере)

Показывает **ВСЕ** страницы:

```
📂 MAIN:
  📱 🏠 Главная → index.html
  📱 📋 Задачи → tasks.html
  📱 📅 События → events.html  
  📱 🛒 Покупки → shopping.html
  🖥️ 📅 Встречи → /dashboard/meetings.html
  🖥️ 📊 Отчеты → /dashboard/reports.html
  🖥️ 📁 Проекты → /dashboard/projects.html
  🖥️ 📝 Заметки → /dashboard/notes.html

📂 PROJECTS:
  📱 📁 Все проекты → project_select.html
  📱 ➕ Создать проект → project_create.html

📂 CREATE:
  📱 📝 Новая задача → task_add.html
  📱 📅 Новое событие → event_create.html
  📱 🛒 Добавить покупку → shopping.html

📂 SETTINGS:
  📱 ⚙️ Настройки → settings.html
  📱 🌍 Часовой пояс → timezone-settings.html

📂 TOOLS:
  🖥️ 🎨 UI Kit → /dashboard/ui-kit.html
```

## Как добавить новые пункты навигации

### 1. Добавление страницы только для WebApp

```sql
-- Подключение к базе данных
docker-compose exec db psql -U postgres -d telegram_app

-- Добавление пункта навигации
INSERT INTO navigation_items (
    title, url, icon, description, 
    sort_order, category, is_active, is_visible
) VALUES (
    'Профиль',                    -- Название
    'profile.html',               -- URL БЕЗ /dashboard/ = только WebApp
    '👤',                         -- Иконка
    'Профиль пользователя',       -- Описание
    13,                           -- Порядок сортировки
    'main',                       -- Категория
    TRUE,                         -- Активен
    TRUE                          -- Видимый
);
```

### 2. Добавление страницы только для Dashboard

```sql
INSERT INTO navigation_items (
    title, url, icon, description, 
    sort_order, category, is_active, is_visible
) VALUES (
    'Аналитика',                     -- Название
    '/dashboard/analytics.html',     -- URL С /dashboard/ = только Dashboard
    '📊',                            -- Иконка
    'Страница аналитики',            -- Описание
    45,                              -- Порядок сортировки
    'main',                          -- Категория
    TRUE,                            -- Активен
    TRUE                             -- Видимый
);
```

### 3. Добавление страницы для обеих платформ

```sql
INSERT INTO navigation_items (
    title, url, icon, description, 
    sort_order, category, is_active, is_visible
) VALUES (
    'Календарь',                  -- Название
    'calendar.html',              -- URL БЕЗ /dashboard/ = показывается везде
    '📅',                         -- Иконка
    'Общий календарь',            -- Описание
    14,                           -- Порядок сортировки
    'main',                       -- Категория
    TRUE,                         -- Активен
    TRUE                          -- Видимый
);
```

## Практические примеры SQL команд

### Просмотр всей навигации

```sql
SELECT 
    id, title, url, category, sort_order, is_active,
    CASE 
        WHEN url LIKE '/dashboard/%' THEN '🖥️ Dashboard'
        ELSE '📱 WebApp'
    END as type
FROM navigation_items 
ORDER BY category, sort_order;
```

### Отключение пункта навигации

```sql
UPDATE navigation_items 
SET is_active = FALSE 
WHERE title = 'UI Kit';
```

### Изменение порядка сортировки

```sql
UPDATE navigation_items 
SET sort_order = 5 
WHERE title = 'Покупки';
```

### Перемещение в другую категорию

```sql
UPDATE navigation_items 
SET category = 'tools' 
WHERE title = 'Настройки';
```

### Удаление пункта навигации

```sql
DELETE FROM navigation_items 
WHERE title = 'Старая страница';
```

## Тестирование навигации

### Проверка API

```bash
# WebApp навигация (фильтрованная)
curl "http://localhost:8000/api/navigation?category=main" | python3 -m json.tool

# Все пункты навигации
curl "http://localhost:8000/api/navigation" | python3 -m json.tool
```

### Проверка в браузере

1. Откройте http://localhost:8000/dashboard/
2. Навигация должна загрузиться автоматически
3. Проверьте консоль браузера на ошибки

### Проверка в Telegram WebApp

1. Откройте WebApp в Telegram
2. Навигация должна показывать только WebApp страницы
3. Проверьте, что Dashboard страницы не отображаются

## Структура категорий

### `main` - Основные страницы
- Самые важные функции приложения
- Отображаются первыми
- sort_order: 1-50

### `projects` - Управление проектами  
- Создание и управление проектами
- sort_order: 51-60

### `create` - Создание контента
- Быстрое создание задач, событий и т.д.
- sort_order: 61-70

### `settings` - Настройки
- Пользовательские настройки
- sort_order: 71-80

### `tools` - Инструменты
- Вспомогательные инструменты
- sort_order: 81-90

### `admin` - Администрирование
- Административные функции
- sort_order: 91-100

## Рекомендации

### Именование URL

**Для WebApp (Telegram):**
- `tasks.html` ✅
- `profile.html` ✅
- `settings.html` ✅

**Для Dashboard (Браузер):**
- `/dashboard/analytics.html` ✅
- `/dashboard/admin.html` ✅
- `/dashboard/reports.html` ✅

### Порядок сортировки

- Используйте шаг 10 для основных пунктов (10, 20, 30...)
- Оставляйте место для вставки новых пунктов
- Группируйте связанные пункты рядом

### Иконки

- Используйте emoji для простоты
- Будьте последовательны в выборе иконок
- Избегайте слишком похожих иконок

### Категории

- Не создавайте слишком много категорий
- Группируйте логически связанные пункты
- Используйте понятные названия категорий

## Отладка проблем

### Навигация не загружается

1. Проверьте подключение к базе данных
2. Проверьте API: `curl http://localhost:8000/api/navigation`
3. Проверьте консоль браузера на ошибки JavaScript

### Пункт не отображается

1. Проверьте `is_active = TRUE` и `is_visible = TRUE`
2. Проверьте правильность URL
3. Проверьте категорию и порядок сортировки

### Неправильная фильтрация WebApp/Dashboard

1. Проверьте URL - должен начинаться с `/dashboard/` для Dashboard-only
2. Проверьте логику фильтрации в `webapp-navigation-loader.js`
3. Очистите кеш браузера и localStorage