# Исправление стилей WebApp

## Описание проблем

При сравнении страницы `static/index.html` с `dashboard/main.html` были выявлены проблемы со стилями:

1. **Отсутствие отступа между чекбоксом и названием задачи**
2. **Слишком большие заголовки групп** ("Просроченные", "На сегодня")

## Внесенные исправления

### 1. Отступ для чекбоксов
**Файл:** `/static/webapp-styles.css` (строка 3212)

```css
/* Было: */
.checkbox {
    width: 18px;
    height: 18px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 4px;
    cursor: pointer;
    transition: all var(--transition-fast);
    flex-shrink: 0;
}

/* Стало: */
.checkbox {
    width: 18px;
    height: 18px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 4px;
    cursor: pointer;
    transition: all var(--transition-fast);
    flex-shrink: 0;
    margin-right: 12px; /* ← Добавлен отступ */
}
```

### 2. Уменьшение заголовков групп
**Файл:** `/static/webapp-styles.css` (строка 3184)

```css
/* Было: */
.tasks-group-header {
    padding: 10px 15px;
    font-weight: 600;
    align-items: center;
    gap: 8px;
    border-radius: var(--radius-medium) 8px 0 0;
    margin-bottom: 8px;
    display: flex;
}

/* Стало: */
.tasks-group-header {
    padding: 6px 12px;        /* ← Уменьшен padding */
    font-weight: 600;
    align-items: center;
    gap: 8px;
    border-radius: var(--radius-medium) 8px 0 0;
    margin-bottom: 4px;       /* ← Уменьшен margin */
    display: flex;
    font-size: 14px;          /* ← Добавлен размер шрифта */
    color: var(--text-secondary); /* ← Приглушенный цвет */
}
```

### 3. Оптимизация счетчиков
**Файл:** `/static/webapp-styles.css` (строка 3196)

```css
/* Было: */
.tasks-group-header .section-count {
    margin-left: 6px;
    background: var(--bg-accent);
    color: white;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
}

/* Стало: */
.tasks-group-header .section-count {
    margin-left: auto;        /* ← Выравнивание по правому краю */
    background: var(--bg-accent);
    color: white;
    padding: 1px 6px;         /* ← Уменьшен padding */
    border-radius: 10px;      /* ← Более круглый */
    font-size: 11px;          /* ← Меньший размер шрифта */
    min-width: 18px;          /* ← Минимальная ширина */
    text-align: center;       /* ← Центрирование текста */
}
```

### 4. Обновление версии CSS
- Версия CSS обновлена с `v=12` на `v=13`
- Обновлены все HTML файлы WebApp для принудительного обновления кэша

## Результат

✅ **Улучшенная читаемость** - четкий отступ между чекбоксом и текстом  
✅ **Компактные заголовки** - заголовки групп занимают меньше места  
✅ **Лучшая визуальная иерархия** - приглушенный цвет заголовков  
✅ **Оптимизированные счетчики** - компактные и выровненные по правому краю  

## Затронутые файлы

### CSS:
- `/static/webapp-styles.css` - основные исправления стилей

### HTML (обновлена версия CSS):
- `index.html`, `tasks.html`, `events.html`
- `task.html`, `task_add.html`, `shopping.html`
- `task_edit.html`, `settings.html`
- `admin/index.html`, `admin/tables.html`
- И другие файлы WebApp

## Совместимость

Изменения затрагивают только WebApp (`/static/`) и не влияют на dashboard (`/dashboard/`).

## Тестирование

Для проверки исправлений:
1. Открыть `static/index.html`
2. Проверить отступы между чекбоксами и названиями задач
3. Убедиться, что заголовки групп стали компактнее
4. Проверить выравнивание счетчиков по правому краю