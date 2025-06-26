# 🎨 Система тем в стиле Telegram

Единая система тем для всех страниц проекта с поддержкой светлой и темной темы в стиле Telegram.

## 📁 Структура файлов

### Основные файлы тем:
- `dashboard/themes.css` - Основной файл с CSS переменными и стилями тем
- `dashboard/theme-manager.js` - Менеджер тем для обычных веб-страниц
- `static/themes.css` - Копия основного файла тем для WebApp
- `static/theme-manager.js` - Копия менеджера тем для WebApp
- `static/webapp-theme-manager.js` - Специальный менеджер тем для Telegram WebApp

## 🎨 Цветовая палитра Telegram

### Светлая тема:
- **Основной фон**: `#ffffff` (белый)
- **Вторичный фон**: `#f8f9fa` (светло-серый)
- **Фон карточек**: `#ffffff` (белый)
- **Основной текст**: `#000000` (черный)
- **Вторичный текст**: `#6c757d` (серый)
- **Telegram синий**: `#0088cc`
- **Telegram фиолетовый**: `#8b5cf6`

### Темная тема:
- **Основной фон**: `#212121` (темно-серый)
- **Вторичный фон**: `#2c2c2c` (серый)
- **Фон карточек**: `#1e1e1e` (почти черный)
- **Основной текст**: `#ffffff` (белый)
- **Вторичный текст**: `#b0b0b0` (светло-серый)
- **Telegram синий**: `#54a9eb`
- **Telegram фиолетовый**: `#a855f7`

## 🔧 CSS переменные

```css
/* Основные цвета */
--bg-primary: основной фон
--bg-secondary: вторичный фон
--bg-card: фон карточек
--bg-hover: фон при наведении
--text-primary: основной текст
--text-secondary: вторичный текст
--text-inverse: инверсный текст

/* Telegram цвета */
--tg-blue: основной синий Telegram
--tg-blue-dark: темный синий
--tg-purple: фиолетовый Telegram
--tg-red: красный Telegram

/* Семантические цвета */
--success: зеленый (успех)
--warning: оранжевый (предупреждение)
--error: красный (ошибка)

/* Границы и тени */
--border-light: светлые границы
--border-medium: средние границы
--shadow-light: легкие тени
--shadow-medium: средние тени
--shadow-dark: темные тени

/* Анимации */
--transition-fast: быстрые переходы (0.15s)
--transition-normal: обычные переходы (0.3s)
```

## 📱 Использование в HTML

### Для обычных веб-страниц (dashboard):
```html
<link rel="stylesheet" href="themes.css">
<script src="theme-manager.js"></script>
```

### Для Telegram WebApp (static):
```html
<link rel="stylesheet" href="themes.css">
<script src="webapp-theme-manager.js"></script>
```

## 🎛️ JavaScript API

### Основные функции:
```javascript
// Переключить тему
toggleTheme()

// Установить конкретную тему
setTheme('dark') // или 'light'

// Получить текущую тему
getCurrentTheme()

// Проверить, темная ли тема
isDarkTheme()

// Сбросить к автоматической теме
resetToAutoTheme() // только для WebApp
```

### События:
```javascript
// Слушать изменения темы
document.addEventListener('themechange', (e) => {
    console.log('Новая тема:', e.detail.theme);
});
```

## 🔄 Автоматическое переключение

Система автоматически определяет тему в следующем порядке:
1. Сохраненная пользователем тема
2. Тема Telegram WebApp (только для WebApp)
3. Системная тема браузера
4. Светлая тема по умолчанию

## ⌨️ Горячие клавиши

- `Ctrl/Cmd + Shift + T` - переключить тему

## 🎨 Кнопка переключения тем

Автоматически создается на всех страницах:
- **Обычные страницы**: фиксированная кнопка в правом верхнем углу
- **WebApp**: адаптированная под Telegram интерфейс

## 📄 Обновленные страницы

### Dashboard (веб-версия):
- ✅ `dashboard/index.html` - авторизация
- ✅ `dashboard/main.html` - главная страница
- ✅ `dashboard/tasks.html` - список задач
- ✅ `local_auth.html` - локальная авторизация

### WebApp (Telegram):
- ✅ `static/index.html` - главная
- ✅ `static/tasks.html` - задачи
- ✅ `static/events.html` - события
- ✅ `static/shopping.html` - покупки
- ✅ `static/settings.html` - настройки
- ✅ `static/task_add.html` - добавление задачи
- ✅ `static/task_edit.html` - редактирование задачи
- ✅ `static/task.html` - просмотр задачи
- ✅ `static/project.html` - проект
- ✅ `static/project_select.html` - выбор проекта
- ✅ `static/project_create.html` - создание проекта
- ✅ `static/event_create.html` - создание события

## 🔧 Интеграция с Telegram WebApp

WebApp версия автоматически:
- Синхронизируется с темой Telegram
- Обновляет цвета заголовка и фона
- Использует Haptic Feedback при переключении
- Адаптируется под цветовую схему Telegram

## 🎯 Особенности

1. **Единообразие**: все страницы используют одну систему тем
2. **Адаптивность**: автоматическое определение предпочтений пользователя
3. **Производительность**: CSS переменные для быстрого переключения
4. **Доступность**: поддержка системных настроек
5. **Telegram интеграция**: полная совместимость с WebApp

## 🚀 Быстрый старт

1. Подключите CSS файл тем
2. Подключите соответствующий JS менеджер тем
3. Используйте CSS переменные в своих стилях
4. Тема будет работать автоматически!

Пример:
```css
.my-element {
    background-color: var(--bg-secondary);
    color: var(--text-primary);
    border: 1px solid var(--border-light);
    transition: all var(--transition-fast);
}
```

## 🎨 Результат

Теперь все страницы проекта имеют:
- ✨ Красивую темную тему в стиле Telegram
- 🔄 Плавные переходы между темами
- 📱 Адаптацию под Telegram WebApp
- 🎛️ Удобное переключение тем
- 🎯 Единообразный дизайн