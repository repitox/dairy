# Упрощение структуры навигации

## Обзор

Выполнена миграция для упрощения структуры таблицы `navigation_items`. Убраны избыточные поля, оставлены только необходимые для работы.

## Новая структура таблицы

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | SERIAL PRIMARY KEY | Уникальный идентификатор |
| `title` | VARCHAR(100) NOT NULL | Название пункта меню |
| `url` | VARCHAR(255) NOT NULL | Ссылка на страницу |
| `platform` | VARCHAR(20) NOT NULL | Платформа: 'dashboard' или 'webapp' |
| `sort_order` | INTEGER DEFAULT 0 | Порядок сортировки (чем меньше, тем выше) |
| `parent_id` | INTEGER DEFAULT NULL | ID родительского элемента (для иерархии) |
| `is_active` | BOOLEAN DEFAULT TRUE | Активность элемента (отображается или нет) |

## Изменения

### Удаленные поля
- `icon` - иконки теперь задаются в коде
- `description` - описания не используются
- `is_visible` - заменено на `is_active`
- `category` - заменено на `platform`
- `group_name` - не используется
- `required_role` - права доступа решаются на уровне приложения
- `required_permission` - права доступа решаются на уровне приложения
- `badge_text` - не используется
- `badge_color` - не используется
- `css_classes` - стили задаются в коде
- `attributes` - дополнительные атрибуты не используются
- `created_at` - метаданные не нужны
- `updated_at` - метаданные не нужны
- `created_by` - метаданные не нужны
- `updated_by` - метаданные не нужны

### Новые поля
- `platform` - четкое разделение между dashboard и webapp

## Платформы

### Dashboard
- URL начинается с `/dashboard/`
- Используется для веб-интерфейса в браузере
- Примеры: `/dashboard/main.html`, `/dashboard/tasks.html`

### WebApp
- URL без префикса
- Используется для Telegram WebApp
- Примеры: `index.html`, `tasks.html`

## Индексы

- `idx_navigation_new_platform` - по платформе
- `idx_navigation_new_sort_order` - по порядку сортировки
- `idx_navigation_new_active` - по активности
- `idx_navigation_new_parent` - по родительскому элементу

## Ограничения

- `chk_platform` - проверка, что platform может быть только 'dashboard' или 'webapp'
- Foreign key на `parent_id` для поддержки иерархии

## Миграция

### Локальная разработка
```bash
docker exec -i tg_project-db-1 psql -U postgres -d telegram_app < migrations/20250119_120000_simplify_navigation_structure.sql
```

### Продакшен
```sql
-- Выполнить содержимое файла migrations/20250119_120000_simplify_navigation_structure.sql
```

## Результат миграции

- ✅ Упрощена структура таблицы с 21 поля до 7
- ✅ Четкое разделение между dashboard и webapp
- ✅ Сохранены все активные элементы навигации
- ✅ Подготовлена основа для иерархической навигации (parent_id)

## Статистика после миграции

- 📊 Всего элементов навигации: 18
- 🖥️ Dashboard элементов: 8
- 📱 WebApp элементов: 10

## Использование в коде

### Получение навигации для dashboard
```sql
SELECT id, title, url, sort_order, parent_id 
FROM navigation_items 
WHERE platform = 'dashboard' AND is_active = true 
ORDER BY sort_order;
```

### Получение навигации для webapp
```sql
SELECT id, title, url, sort_order, parent_id 
FROM navigation_items 
WHERE platform = 'webapp' AND is_active = true 
ORDER BY sort_order;
```

### Добавление нового элемента
```sql
INSERT INTO navigation_items (title, url, platform, sort_order, is_active) 
VALUES ('Новая страница', 'new-page.html', 'webapp', 110, true);
```

### Деактивация элемента
```sql
UPDATE navigation_items SET is_active = false WHERE id = 1;
```

## Откат миграции

Если потребуется откат, старая таблица сохранена как `navigation_items_old`:

```sql
BEGIN;
DROP TABLE navigation_items;
ALTER TABLE navigation_items_old RENAME TO navigation_items;
COMMIT;
```

## Дата выполнения

- **Локально**: 2025-01-19 12:00:00
- **Продакшен**: Ожидает выполнения