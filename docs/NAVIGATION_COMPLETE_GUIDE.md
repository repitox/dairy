# Полное руководство по навигации

**Дата создания**: 7 января 2025  
**Версия**: 1.0  
**Статус**: ✅ Готово к использованию

## 🎯 Краткий ответ на ваш вопрос

**Как правильно работать с навигацией?**

1. **Навигация хранится в таблице `navigation_items` в PostgreSQL**
2. **Разделение происходит автоматически по URL:**
   - URL **БЕЗ** `/dashboard/` → показывается в **WebApp (Telegram)**
   - URL **С** `/dashboard/` → показывается только в **Dashboard (браузер)**
   - Все активные пункты показываются в Dashboard

3. **Для управления используйте:**
   - **Веб-интерфейс**: http://localhost:8000/dashboard/navigation-admin.html
   - **SQL команды** через Docker
   - **API**: `/api/navigation`

## 🗂️ Текущая структура навигации

### 📱 WebApp (Telegram) - 10 пунктов
```
📂 MAIN (основные):
  🏠 Главная → index.html
  📋 Задачи → tasks.html  
  📅 События → events.html
  🛒 Покупки → shopping.html

📂 PROJECTS (проекты):
  📁 Все проекты → project_select.html
  ➕ Создать проект → project_create.html

📂 CREATE (создание):
  📝 Новая задача → task_add.html
  📅 Новое событие → event_create.html
  🛒 Добавить покупку → shopping.html

📂 SETTINGS (настройки):
  ⚙️ Настройки → settings.html
  🌍 Часовой пояс → timezone-settings.html
```

### 🖥️ Dashboard (Браузер) - 16 пунктов
```
📂 MAIN (основные):
  📱 🏠 Главная → index.html
  📱 📋 Задачи → tasks.html
  📱 📅 События → events.html  
  📱 🛒 Покупки → shopping.html
  🖥️ 📅 Встречи → /dashboard/meetings.html
  🖥️ 📊 Отчеты → /dashboard/reports.html
  🖥️ 📁 Проекты → /dashboard/projects.html
  🖥️ 📝 Заметки → /dashboard/notes.html

📂 PROJECTS, CREATE, SETTINGS (как в WebApp)

📂 TOOLS (инструменты):
  🖥️ 🎨 UI Kit → /dashboard/ui-kit.html
```

## 🛠️ Способы управления навигацией

### 1. 🌐 Веб-интерфейс (Рекомендуется)

**URL**: http://localhost:8000/dashboard/navigation-admin.html

**Возможности:**
- ✅ Просмотр всех пунктов навигации
- ✅ Добавление новых пунктов
- ✅ Включение/выключение пунктов
- ✅ Удаление пунктов
- ✅ Предварительный просмотр WebApp/Dashboard
- ✅ Автоматическое определение типа по URL

### 2. 💾 SQL команды через Docker

```bash
# Подключение к базе данных
docker-compose exec db psql -U postgres -d telegram_app

# Просмотр всех пунктов
SELECT id, title, url, category, sort_order, is_active FROM navigation_items ORDER BY category, sort_order;

# Добавление нового пункта
INSERT INTO navigation_items (title, url, icon, description, sort_order, category) 
VALUES ('Новая страница', 'new-page.html', '🆕', 'Описание', 15, 'main');

# Отключение пункта
UPDATE navigation_items SET is_active = FALSE WHERE id = 1;

# Удаление пункта
DELETE FROM navigation_items WHERE id = 1;
```

### 3. 🔌 API эндпоинты

```bash
# Получение навигации
curl "http://localhost:8000/api/navigation?category=main"

# Добавление пункта
curl -X POST "http://localhost:8000/api/navigation" \
  -H "Content-Type: application/json" \
  -d '{"title": "Новая страница", "url": "new.html", "icon": "🆕", "category": "main", "sort_order": 15}'

# Обновление пункта
curl -X POST "http://localhost:8000/api/navigation" \
  -H "Content-Type: application/json" \
  -d '{"id": 1, "is_active": false}'

# Удаление пункта
curl -X DELETE "http://localhost:8000/api/navigation" \
  -H "Content-Type: application/json" \
  -d '{"id": 1}'
```

## 📋 Практические примеры

### Добавить страницу только для WebApp

```sql
INSERT INTO navigation_items (title, url, icon, description, sort_order, category) 
VALUES ('Профиль', 'profile.html', '👤', 'Профиль пользователя', 13, 'main');
```
**Результат**: Страница появится в Telegram WebApp и Dashboard

### Добавить страницу только для Dashboard

```sql
INSERT INTO navigation_items (title, url, icon, description, sort_order, category) 
VALUES ('Аналитика', '/dashboard/analytics.html', '📊', 'Страница аналитики', 45, 'main');
```
**Результат**: Страница появится только в Dashboard (браузер)

### Временно скрыть пункт навигации

```sql
UPDATE navigation_items SET is_active = FALSE WHERE title = 'UI Kit';
```
**Результат**: Пункт исчезнет из обеих навигаций

### Изменить порядок отображения

```sql
UPDATE navigation_items SET sort_order = 5 WHERE title = 'Покупки';
```
**Результат**: Пункт "Покупки" переместится выше в списке

## 🎨 Настройка внешнего вида

### Иконки
- Используйте emoji: 🏠 📋 📅 🛒 ⚙️
- Или CSS классы: `fa-home`, `icon-tasks`

### Категории
- `main` - основные страницы (показываются первыми)
- `projects` - управление проектами
- `create` - создание контента
- `settings` - настройки
- `tools` - инструменты
- `admin` - администрирование

### Порядок сортировки (sort_order)
- **1-10**: Основные WebApp страницы
- **11-20**: Дополнительные WebApp страницы
- **30-50**: Dashboard основные страницы
- **51-70**: Dashboard дополнительные страницы
- **71-90**: Инструменты и утилиты

## 🔧 Отладка и диагностика

### Проверка состояния навигации

```bash
# Количество пунктов в базе
docker-compose exec db psql -U postgres -d telegram_app -c "SELECT COUNT(*) FROM navigation_items;"

# Активные пункты по типам
docker-compose exec db psql -U postgres -d telegram_app -c "
SELECT 
    CASE WHEN url LIKE '/dashboard/%' THEN 'Dashboard' ELSE 'WebApp' END as type,
    COUNT(*) as count
FROM navigation_items 
WHERE is_active = TRUE 
GROUP BY (url LIKE '/dashboard/%');"
```

### Тестирование API

```bash
# Основная навигация
curl -s "http://localhost:8000/api/navigation?category=main" | python3 -m json.tool

# Проверка конкретного пункта
curl -s "http://localhost:8000/api/navigation" | jq '.navigation[] | select(.title=="Главная")'
```

### Проверка в браузере

1. Откройте http://localhost:8000/dashboard/
2. Откройте DevTools (F12) → Console
3. Выполните: `console.log(window.navigationData)`
4. Проверьте загрузку навигации

### Очистка кеша

```javascript
// В консоли браузера
localStorage.removeItem('navigation_cache');
localStorage.removeItem('webapp_navigation_cache');
location.reload();
```

## 🚨 Частые проблемы и решения

### Проблема: Пункт не отображается в WebApp
**Решение**: Проверьте, что URL не содержит `/dashboard/`

### Проблема: Пункт не отображается в Dashboard
**Решение**: Проверьте `is_active = TRUE` и `is_visible = TRUE`

### Проблема: Неправильный порядок пунктов
**Решение**: Проверьте `sort_order` - меньшие числа отображаются первыми

### Проблема: API возвращает ошибку
**Решение**: 
1. Проверьте, что Docker контейнеры запущены
2. Проверьте подключение к базе данных
3. Проверьте логи: `docker-compose logs app`

## 📚 Дополнительные ресурсы

- **Подробное руководство**: `/docs/NAVIGATION_GUIDE.md`
- **Примеры использования**: `/docs/NAVIGATION_EXAMPLES.md`
- **API документация**: `/docs/API_NAVIGATION_SYSTEM.md`
- **Веб-интерфейс**: http://localhost:8000/dashboard/navigation-admin.html

## 🎉 Заключение

Система навигации полностью настроена и готова к использованию:

1. **WebApp (Telegram)** автоматически показывает только релевантные страницы
2. **Dashboard (браузер)** показывает все доступные страницы
3. **Управление** возможно через веб-интерфейс, SQL или API
4. **Кеширование** обеспечивает быструю загрузку
5. **Fallback режим** гарантирует работу даже при проблемах с БД

**Для добавления новой страницы просто добавьте запись в таблицу `navigation_items` с правильным URL - система автоматически определит, где её показывать!**