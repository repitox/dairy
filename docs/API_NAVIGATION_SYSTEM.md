# API Navigation System

**Дата создания**: 31 января 2025  
**Версия**: 1.0  
**Статус**: ✅ Готово к использованию

## Обзор

Реализована централизованная система управления навигацией dashboard через API с хранением данных в PostgreSQL. Система предоставляет динамическую навигацию с кешированием, fallback-режимом и предотвращением прыжков контента.

## Основные компоненты

### 1. База данных

**Таблица**: `navigation_items`

```sql
-- Основные поля
id SERIAL PRIMARY KEY
title VARCHAR(100) NOT NULL              -- Название пункта меню
url VARCHAR(255) NOT NULL                -- Ссылка (relative path)
icon VARCHAR(50)                         -- Иконка (emoji или класс)
description TEXT                         -- Описание для tooltip

-- Позиционирование и отображение
sort_order INTEGER DEFAULT 0            -- Порядок сортировки
is_active BOOLEAN DEFAULT TRUE          -- Активен ли пункт
is_visible BOOLEAN DEFAULT TRUE         -- Видимый ли пункт

-- Группировка и категории
category VARCHAR(50) DEFAULT 'main'     -- Категория (main, admin, tools)
group_name VARCHAR(50)                  -- Группа для подменю
parent_id INTEGER                       -- Родительский элемент

-- Дополнительные атрибуты
badge_text VARCHAR(20)                  -- Текст бейджа
badge_color VARCHAR(20)                 -- Цвет бейджа
css_classes TEXT                        -- Дополнительные CSS классы
attributes JSONB DEFAULT '{}'          -- Дополнительные атрибуты

-- Метаданные
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
created_by INTEGER
updated_by INTEGER
```

### 2. API Endpoints

#### GET `/api/navigation`

Получение пунктов навигации.

**Параметры**:
- `user_id` (optional) - ID пользователя для проверки прав доступа
- `category` (optional, default="main") - Категория навигации

**Ответ**:
```json
{
  "navigation": [
    {
      "id": 1,
      "title": "Главная",
      "url": "/dashboard/main.html",
      "icon": "🏠",
      "description": "Главная страница dashboard",
      "sort_order": 10,
      "badge_text": null,
      "badge_color": null,
      "css_classes": null,
      "attributes": {},
      "category": "main",
      "group_name": null,
      "parent_id": null,
      "children": []
    }
  ],
  "category": "main",
  "total_items": 8,
  "cache_key": "nav_main_8",
  "timestamp": 1753965167
}
```

#### POST `/api/navigation`

Создание или обновление пункта навигации (для админ-панели).

**Тело запроса**:
```json
{
  "user_id": 12345,
  "title": "Новый пункт",
  "url": "/dashboard/new-page.html",
  "icon": "🆕",
  "sort_order": 90,
  "category": "main"
}
```

### 3. JavaScript Loader

**Файл**: `dashboard/navigation-api-loader.js`

#### Возможности:
- ✅ Автоматическая загрузка навигации при DOMContentLoaded
- ✅ Кеширование в localStorage (TTL: 30 минут)
- ✅ Skeleton анимация для предотвращения прыжков
- ✅ Fallback навигация при ошибках API
- ✅ Таймаут загрузки (3 секунды)
- ✅ Иерархическая структура (parent/child)
- ✅ Мобильная адаптация

#### Использование:
```html
<!-- Подключение стилей и скрипта -->
<link rel="stylesheet" href="navigation-api.css">
<script src="navigation-api-loader.js"></script>

<!-- Навигация загружается автоматически -->
<!-- Контент страницы будет обернут в api-main-content -->
```

#### API загрузчика:
```javascript
// Принудительная загрузка
window.ApiNavigationLoader.load();

// Очистка кеша
window.ApiNavigationLoader.clearCache();

// Проверка статуса
console.log(window.ApiNavigationLoader.isLoaded());

// Событие завершения загрузки
document.addEventListener('apiNavigationLoaded', function(event) {
    console.log('Навигация загружена:', event.detail.navigationItems);
});
```

### 4. CSS Стили

**Файл**: `dashboard/navigation-api.css`

#### Основные классы:
- `.api-navbar` - Верхняя панель навигации
- `.api-sidebar` - Боковая панель с меню
- `.api-main-content` - Обертка для основного контента
- `.api-navigation-skeleton` - Skeleton анимация
- `.api-nav-item` - Пункт меню
- `.api-nav-item.active` - Активный пункт меню

## Преимущества новой системы

### 🎯 Централизованное управление
- Все пункты навигации хранятся в БД
- Изменения применяются мгновенно для всех пользователей
- Возможность персонализации по пользователям/ролям

### ⚡ Производительность
- Кеширование в localStorage (30 минут TTL)
- Skeleton предотвращает прыжки контента
- Preload API для быстрой загрузки

### 🛡️ Надежность
- Fallback навигация при ошибках API
- Таймаут загрузки для предотвращения зависания
- Graceful degradation

### 📱 Адаптивность
- Мобильная оптимизация
- Responsive layout
- Touch-friendly интерфейс

## Миграция с предыдущей системы

### Шаг 1: Применить миграцию БД
```bash
# В Docker
docker-compose exec app python3 -c "
from db import get_conn
with open('database/migrations/041_create_navigation_table_simple.sql', 'r') as f:
    sql = f.read()
conn = get_conn()
cursor = conn.cursor()
cursor.execute(sql)
conn.commit()
cursor.close()
conn.close()
"
```

### Шаг 2: Обновить HTML страницы
```html
<!-- Старый способ -->
<div id="navbar-container"></div>
<script src="navbar-component.js"></script>

<!-- Новый способ -->
<link rel="stylesheet" href="navigation-api.css">
<script src="navigation-api-loader.js"></script>
<!-- Навигация добавляется автоматически -->
```

### Шаг 3: Удалить старые файлы
- `navbar-component.js`
- `navigation-preload.js`
- Статические данные навигации

## Управление навигацией

### Добавление нового пункта (через БД)
```sql
INSERT INTO navigation_items (
    title, url, icon, sort_order, category, description
) VALUES (
    'Новая страница', '/dashboard/new.html', '🆕', 85, 'main', 'Описание новой страницы'
);
```

### Изменение порядка
```sql
UPDATE navigation_items 
SET sort_order = 15 
WHERE title = 'Задачи';
```

### Скрытие пункта
```sql
UPDATE navigation_items 
SET is_visible = FALSE 
WHERE title = 'UI Kit';
```

### Добавление подменю
```sql
-- Сначала создаем родительский пункт
INSERT INTO navigation_items (title, url, icon, sort_order) 
VALUES ('Отчеты', '#', '📊', 80);

-- Затем дочерние пункты
INSERT INTO navigation_items (title, url, icon, sort_order, parent_id) 
VALUES ('Статистика', '/dashboard/stats.html', '📈', 81, 
        (SELECT id FROM navigation_items WHERE title = 'Отчеты'));
```

## Тестирование

### Тестовая страница
Доступна по адресу: `/dashboard/main-api-test.html`

Показывает:
- ✅ Статус загрузки навигации
- 📊 Источник данных (API/кеш)
- ⏱️ Время загрузки
- 🔢 Количество пунктов

### API тестирование
```bash
# Получение навигации
curl "http://localhost:8000/api/navigation?category=main"

# Создание нового пункта
curl -X POST "http://localhost:8000/api/navigation" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "title": "Test", "url": "/test", "icon": "🧪"}'
```

## Troubleshooting

### API не отвечает
1. Проверить статус Docker: `docker-compose ps`
2. Перезапустить сервис: `docker-compose restart app`
3. Проверить логи: `docker-compose logs app`

### Навигация не отображается
1. Открыть DevTools → Console
2. Проверить ошибки JavaScript
3. Убедиться, что файлы CSS/JS загружены

### Fallback режим
- Проверить подключение к БД
- Убедиться, что таблица `navigation_items` существует
- Проверить данные в таблице

## Планы развития

### v1.1 - Расширенные возможности
- [ ] Роли и разрешения для пунктов меню
- [ ] Группировка пунктов в категории
- [ ] Кастомные иконки и темы

### v1.2 - Админ-панель
- [ ] Веб-интерфейс для управления навигацией
- [ ] Drag & drop изменение порядка
- [ ] Preview изменений

### v1.3 - Персонализация
- [ ] Пользовательские настройки навигации
- [ ] Избранные пункты
- [ ] Скрытие ненужных разделов

---

**Система готова к использованию в продакшене! 🚀**