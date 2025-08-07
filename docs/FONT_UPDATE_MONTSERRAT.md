# Обновление шрифта WebApp на Montserrat

## Описание изменений

Обновлен основной шрифт в Telegram WebApp с системного шрифта на Google Fonts Montserrat для улучшения визуального единообразия и современного внешнего вида.

## Внесенные изменения

### 1. Подключение Google Fonts
**Файл:** `/static/webapp-styles.css`
- ✅ Добавлен импорт Montserrat: `@import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,100..900;1,100..900&display=swap');`
- ✅ Подключены все веса шрифта (100-900) и курсив

### 2. Обновление font-family
**Файл:** `/static/webapp-styles.css` (строка 90)
```css
/* Было: */
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;

/* Стало: */
font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
```

### 3. Обновление версии CSS
**Обновлены все HTML файлы WebApp:**
- ✅ Версия CSS изменена с `v=11` на `v=12`
- ✅ Обновлены файлы: `index.html`, `tasks.html`, `events.html`, `task.html`, `task_add.html`, `shopping.html`, `task_edit.html` и другие
- ✅ Обновлены файлы в папке `/admin/`

## Технические детали

### Fallback шрифты
Сохранены системные шрифты как fallback на случай, если Montserrat не загрузится:
- macOS: `-apple-system`, `BlinkMacSystemFont`
- Windows: `'Segoe UI'`
- Android: `Roboto`
- Linux: `Ubuntu`, `Cantarell`
- Общий fallback: `sans-serif`

### Моноширинный шрифт
Для команд регистрации сохранен `'Courier New', monospace` (строка 3311) - это корректно для отображения кода.

### Производительность
- Используется `display=swap` для быстрой загрузки
- Подключены только необходимые веса шрифта
- Сохранены fallback шрифты для мгновенного отображения

## Результат

✅ **Единообразный дизайн** - все страницы WebApp используют Montserrat  
✅ **Современный внешний вид** - улучшенная типографика  
✅ **Быстрая загрузка** - оптимизированное подключение шрифта  
✅ **Совместимость** - fallback на системные шрифты  

## Проверка

Для проверки корректности подключения шрифта:
1. Открыть любую страницу WebApp
2. В DevTools проверить вкладку Network - должен загружаться Montserrat
3. В Elements проверить computed styles - font-family должен показывать Montserrat

## Версионирование

- **CSS версия:** обновлена с v11 на v12
- **Дата изменений:** 28 января 2025
- **Затронутые файлы:** все HTML файлы в `/static/`