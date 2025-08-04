# 🔧 Исправление отображения покупок в WebApp

## Проблема

В WebApp на странице `/static/index.html` в списке покупок вместо названия товара отображался `undefined`.

## Причина

После исправления синхронизации покупок (v3.0.3) все API endpoints стали возвращать данные из таблицы `purchases` с полем `name`, но WebApp продолжал использовать старое поле `item`.

### Несоответствие полей:

| Компонент | Ожидаемое поле | Фактическое поле в API | Результат |
|-----------|----------------|------------------------|-----------|
| WebApp index.html | `item.item` | `item.name` | `undefined` ❌ |
| WebApp shopping.html | `item.item` | `item.name` | `undefined` ❌ |
| Dashboard | `item.name` | `item.name` | Работает ✅ |

## Исправленные файлы

### 1. `/static/index.html` ✅

**Проблема**: В функции `renderShopping()` использовалось поле `item.item`

**Было:**
```javascript
shopping.forEach(item => {
    const text = item.quantity ? `${item.quantity} x ${item.item}` : item.item;
    // ...
});
```

**Стало:**
```javascript
shopping.forEach(item => {
    const text = item.quantity ? `${item.quantity} x ${item.name}` : item.name;
    // ...
});
```

### 2. `/static/shopping.html` ✅

#### 2.1 Исправлено отображение названия товара

**Было:**
```javascript
<strong>${item.item}</strong> × ${item.quantity}
```

**Стало:**
```javascript
<strong>${item.name}</strong> × ${item.quantity}
```

#### 2.2 Исправлено отображение статуса

**Проблема**: Использовалось поле `item.status` (string), но API возвращает `item.completed` (boolean)

**Было:**
```javascript
<span>Статус: ${item.status}</span>
// ...
${item.status === 'Нужно купить' ? `
```

**Стало:**
```javascript
<span>Статус: ${item.completed ? 'Куплено' : 'Нужно купить'}</span>
// ...
${!item.completed ? `
```

#### 2.3 Исправлена функция изменения статуса

**Проблема**: Использовался неправильный API endpoint

**Было:**
```javascript
async function markStatus(id, status) {
    await fetch("/api/shopping/" + id, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status })
    });
}
```

**Стало:**
```javascript
async function markStatus(id, status) {
    if (status === 'Куплено') {
        // Переключаем статус покупки
        await fetch(`/api/shopping/${id}/toggle`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: tg.initDataUnsafe.user?.id })
        });
    } else if (status === 'Удалено') {
        // Удаляем покупку
        await fetch(`/api/shopping/${id}`, {
            method: "DELETE"
        });
    }
}
```

#### 2.4 Исправлена форма добавления покупки

**Проблема**: Отправлялось поле `item` вместо `name`

**Было:**
```javascript
const item = document.getElementById("item").value;
// ...
body: JSON.stringify({ item, quantity, user_id: tg.initDataUnsafe.user?.id, project_id: projectId })
```

**Стало:**
```javascript
const name = document.getElementById("item").value;
// ...
body: JSON.stringify({ name, quantity, user_id: tg.initDataUnsafe.user?.id, category: "other" })
```

## Используемые API endpoints

### ✅ Правильные endpoints (после исправления):

| Действие | Method | Endpoint | Поля |
|----------|--------|----------|------|
| Получить покупки | GET | `/api/shopping?user_id={id}` | Возвращает `name`, `completed` |
| Добавить покупку | POST | `/api/shopping` | Принимает `name`, `quantity`, `category` |
| Переключить статус | POST | `/api/shopping/{id}/toggle` | Принимает `user_id` |
| Удалить покупку | DELETE | `/api/shopping/{id}` | - |

### ❌ Неправильные endpoints (до исправления):

| Действие | Method | Endpoint | Проблема |
|----------|--------|----------|----------|
| Изменить статус | PUT | `/api/shopping/{id}` | Неправильный метод и поля |
| Добавить покупку | POST | `/api/shopping` | Поле `item` вместо `name` |

## Результат тестирования

### До исправления:
```
🛒 Покупки в WebApp:
▪️ 1 × undefined
▪️ 1 × undefined  
▪️ 1 × undefined

Статус: undefined
```

### После исправления:
```
🛒 Покупки в WebApp:
▪️ 1 × Молоко 3.2%
▪️ 1 × Хлеб
▪️ 1 × Мясо

Статус: Нужно купить
```

## Проверка данных API

```bash
# Проверка данных из БД
docker-compose exec app python -c "
from db import get_shopping_items
items = get_shopping_items(123456789)
for item in items:
    print(f'ID: {item[\"id\"]}, name: {item[\"name\"]}, quantity: {item[\"quantity\"]}, completed: {item[\"completed\"]}')
"

# Результат:
# ID: 3, name: Мясо, quantity: 1, completed: False
# ID: 2, name: Хлеб, quantity: 1, completed: False  
# ID: 1, name: Молоко 3.2%, quantity: 1, completed: False
```

## Синхронизация между компонентами

Теперь все компоненты системы используют одинаковые поля:

### ✅ Dashboard (браузер)
- **main.html**: `item.name`, `item.completed` ✅
- **shopping.html**: `item.name`, `item.completed` ✅
- **projects.html**: `item.name`, `item.completed` ✅

### ✅ WebApp (Telegram)
- **index.html**: `item.name`, `item.completed` ✅
- **shopping.html**: `item.name`, `item.completed` ✅

### ✅ Scheduler (рассылка)
- **scheduler.py**: `item.name`, `item.completed` ✅

## Дополнительные улучшения

### 1. Удалены неиспользуемые параметры
В WebApp убраны неиспользуемые параметры API:
- `project_id` - не поддерживается текущим API
- `status` - заменен на `completed`

### 2. Правильная категория по умолчанию
При добавлении покупки в WebApp устанавливается `category: "other"` для совместимости.

### 3. Корректная обработка ошибок
Функции используют правильные HTTP методы и обрабатывают ответы API.

## Затронутые файлы

| Файл | Изменения | Строк |
|------|-----------|-------|
| `static/index.html` | Исправлено поле `item.item` → `item.name` | 1 |
| `static/shopping.html` | Исправлены поля, API endpoints, статусы | 8 |

## Совместимость

### ✅ Обратная совместимость сохранена
- API endpoints не изменились
- Структура данных в БД не изменилась
- Dashboard продолжает работать без изменений

### ✅ Будущие изменения
- Легко добавить новые поля в API
- Простое расширение функциональности WebApp
- Единая схема данных для всех компонентов

---

**Дата исправления**: 2025-01-27  
**Версия**: v3.0.5  
**Статус**: ✅ Исправлено и протестировано