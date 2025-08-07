# Руководство по работе с навигацией

**Дата создания**: 7 января 2025  
**Версия**: 1.0  
**Статус**: ✅ Готово к использованию

## Обзор системы навигации

В проекте реализована централизованная система навигации, которая работает как для **Dashboard** (веб-интерфейс), так и для **WebApp** (Telegram). Навигация хранится в базе данных PostgreSQL и загружается через API.

## Структура навигации

### Таблица `navigation_items`

```sql
CREATE TABLE navigation_items (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,           -- Название пункта меню
    url VARCHAR(500) NOT NULL,             -- Ссылка (относительный путь)
    icon VARCHAR(50),                      -- Иконка (emoji или класс)
    description TEXT,                      -- Описание для tooltip
    sort_order INTEGER DEFAULT 0,         -- Порядок сортировки
    badge_text VARCHAR(50),                -- Текст бейджа
    badge_color VARCHAR(20),               -- Цвет бейджа
    css_classes TEXT,                      -- Дополнительные CSS классы
    attributes JSONB DEFAULT '{}',         -- Дополнительные атрибуты
    category VARCHAR(100) DEFAULT 'main',  -- Категория навигации
    group_name VARCHAR(100),               -- Группа для подменю
    parent_id INTEGER,                     -- Родительский элемент
    is_active BOOLEAN DEFAULT TRUE,        -- Активен ли пункт
    is_visible BOOLEAN DEFAULT TRUE,       -- Видимый ли пункт
    required_role VARCHAR(100),            -- Требуемая роль
    required_permission VARCHAR(100),      -- Требуемое разрешение
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Принцип разделения навигации

### 📱 WebApp (Telegram)
- Показывает только пункты **БЕЗ** `/dashboard/` в URL
- Фильтрация происходит автоматически в `webapp-navigation-loader.js`
- Примеры URL: `index.html`, `tasks.html`, `shopping.html`

### 🖥️ Dashboard (Браузер)
- Показывает **ВСЕ** пункты навигации
- Включает как WebApp страницы, так и Dashboard страницы
- Примеры URL: `/dashboard/meetings.html`, `/dashboard/projects.html`

## Текущая структура навигации

### Категория `main` (основные страницы)

#### WebApp страницы:
- **Главная** (`index.html`) - sort_order: 1
- **Задачи** (`tasks.html`) - sort_order: 2  
- **События** (`events.html`) - sort_order: 3
- **Покупки** (`shopping.html`) - sort_order: 4

#### Dashboard страницы:
- **Встречи** (`/dashboard/meetings.html`) - sort_order: 30
- **Отчеты** (`/dashboard/reports.html`) - sort_order: 35
- **Проекты** (`/dashboard/projects.html`) - sort_order: 40
- **Заметки** (`/dashboard/notes.html`) - sort_order: 60

### Категория `projects` (управление проектами)
- **Все проекты** (`project_select.html`) - sort_order: 5
- **Создать проект** (`project_create.html`) - sort_order: 6

### Категория `create` (создание контента)
- **Новая задача** (`task_add.html`) - sort_order: 7
- **Новое событие** (`event_create.html`) - sort_order: 8
- **Добавить покупку** (`shopping.html`) - sort_order: 9

### Категория `settings` (настройки)
- **Настройки** (`settings.html`) - sort_order: 10
- **Часовой пояс** (`timezone-settings.html`) - sort_order: 11

### Категория `tools` (инструменты)
- **UI Kit** (`/dashboard/ui-kit.html`) - sort_order: 80

## API для работы с навигацией

### GET `/api/navigation`

**Параметры:**
- `category` (optional, default="main") - Категория навигации
- `user_id` (optional) - ID пользователя для проверки прав

**Пример запроса:**
```bash
curl "http://localhost:8000/api/navigation?category=main"
```

**Ответ:**
```json
{
  "navigation": [
    {
      "id": 10,
      "title": "Главная",
      "url": "index.html",
      "icon": "🏠",
      "description": "Главная страница WebApp",
      "sort_order": 1,
      "category": "main",
      "children": []
    }
  ],
  "category": "main",
  "total_items": 8,
  "cache_key": "nav_main_8",
  "timestamp": 1754569196
}
```

## Как добавить новый пункт навигации

### 1. Через SQL (рекомендуется)

```sql
INSERT INTO navigation_items (
    title, url, icon, description, 
    sort_order, category, is_active, is_visible
) VALUES (
    'Новая страница',           -- Название
    'new-page.html',            -- URL (для WebApp) или '/dashboard/new-page.html' (для Dashboard)
    '🆕',                       -- Иконка
    'Описание новой страницы',  -- Описание
    15,                         -- Порядок сортировки
    'main',                     -- Категория
    TRUE,                       -- Активен
    TRUE                        -- Видимый
);
```

### 2. Через Docker

```bash
# Подключение к базе данных
docker-compose exec db psql -U postgres -d telegram_app

# Выполнение SQL команды
INSERT INTO navigation_items (title, url, icon, description, sort_order, category) 
VALUES ('Новая страница', 'new-page.html', '🆕', 'Описание', 15, 'main');
```

## Управление навигацией

### Просмотр всех пунктов навигации

```sql
SELECT id, title, url, category, sort_order, is_active 
FROM navigation_items 
ORDER BY category, sort_order;
```

### Отключение пункта навигации

```sql
UPDATE navigation_items 
SET is_active = FALSE 
WHERE id = 1;
```

### Изменение порядка сортировки

```sql
UPDATE navigation_items 
SET sort_order = 25 
WHERE id = 1;
```

### Перемещение пункта в другую категорию

```sql
UPDATE navigation_items 
SET category = 'tools' 
WHERE id = 1;
```

## Рекомендации по sort_order

- **1-10**: Основные WebApp страницы
- **11-20**: Дополнительные WebApp страницы  
- **21-29**: Резерв для WebApp
- **30-50**: Dashboard основные страницы
- **51-70**: Dashboard дополнительные страницы
- **71-80**: Инструменты и утилиты
- **81-90**: Административные страницы
- **91-100**: Резерв

## Кеширование

Навигация кешируется на стороне клиента:
- **Dashboard**: кеш на 30 минут
- **WebApp**: кеш на 30 минут
- При изменении навигации кеш автоматически обновляется

## Отладка навигации

### Проверка состояния таблицы

```bash
docker-compose exec app python check_navigation_table.py
```

### Тестирование API

```bash
# Основная навигация
curl "http://localhost:8000/api/navigation?category=main"

# Все категории
curl "http://localhost:8000/api/navigation"
```

### Просмотр логов

```bash
docker-compose logs app | grep navigation
```

## Fallback режим

Если база данных недоступна, система автоматически переключается на fallback навигацию:

```javascript
fallback_navigation = [
    {"title": "Главная", "url": "/dashboard/main.html", "icon": "🏠"},
    {"title": "Задачи", "url": "/dashboard/tasks.html", "icon": "📋"},
    {"title": "Встречи", "url": "/dashboard/meetings.html", "icon": "📅"},
    {"title": "Проекты", "url": "/dashboard/projects.html", "icon": "📁"},
    {"title": "Покупки", "url": "/dashboard/shopping.html", "icon": "🛒"},
    {"title": "Заметки", "url": "/dashboard/notes.html", "icon": "📝"},
    {"title": "Настройки", "url": "/dashboard/settings.html", "icon": "⚙️"},
    {"title": "UI Kit", "url": "/dashboard/ui-kit.html", "icon": "🎨"}
]
```

## Примеры использования

### Добавление страницы только для Dashboard

```sql
INSERT INTO navigation_items (title, url, icon, description, sort_order, category) 
VALUES ('Аналитика', '/dashboard/analytics.html', '📊', 'Страница аналитики', 45, 'main');
```

### Добавление страницы только для WebApp

```sql
INSERT INTO navigation_items (title, url, icon, description, sort_order, category) 
VALUES ('Профиль', 'profile.html', '👤', 'Профиль пользователя', 12, 'main');
```

### Создание подменю

```sql
-- Родительский элемент
INSERT INTO navigation_items (title, url, icon, description, sort_order, category) 
VALUES ('Управление', '#', '⚙️', 'Управление системой', 80, 'admin');

-- Дочерние элементы
INSERT INTO navigation_items (title, url, icon, description, sort_order, category, parent_id) 
VALUES ('Пользователи', '/dashboard/users.html', '👥', 'Управление пользователями', 81, 'admin', 
        (SELECT id FROM navigation_items WHERE title = 'Управление'));
```

## Заключение

Система навигации полностью настроена и готова к использованию. Для добавления новых страниц просто добавьте записи в таблицу `navigation_items` с правильными URL:

- **Для WebApp**: используйте относительные пути без `/dashboard/`
- **Для Dashboard**: используйте пути с `/dashboard/` или относительные (будут показаны везде)

Система автоматически разделит навигацию между WebApp и Dashboard на основе URL.