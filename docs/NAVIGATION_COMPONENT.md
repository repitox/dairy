# Компонент навигации Dashboard

## Описание

Универсальный компонент навигации для всех страниц дашборда, который включает в себя:
- Верхнюю навигационную панель (navbar)
- Боковую навигацию (sidebar)
- Мобильное меню
- Автоматическую синхронизацию данных пользователя

## Файлы компонента

- `navigation-component.html` - HTML-разметка и JavaScript функциональность
- `navigation-loader.js` - Загрузчик компонента для автоматического подключения

## Использование

### Подключение к новой странице

1. Добавьте загрузчик в `<head>` или перед закрывающим `</body>`:
```html
<script src="navigation-loader.js"></script>
```

2. Структура HTML страницы:
```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Название страницы - Dashboard</title>
    <link rel="stylesheet" href="dashboard-styles.css">
    <link rel="stylesheet" href="navigation.css">
    <link rel="stylesheet" href="ui-components.css">
</head>

<body>
    <!-- Навигация будет загружена автоматически -->
    
    <!-- Основной контент страницы -->
    <div class="page-container">
        <!-- Ваш контент здесь -->
    </div>

    <script src="navigation-loader.js"></script>
    <script src="auth.js"></script>
    <script>
        // Callback для обработки загруженного пользователя
        window.onUserLoaded = function (user) {
            if (window.NavigationComponent && window.NavigationComponent.updateUserInfo) {
                window.NavigationComponent.updateUserInfo(user);
            }
            // Ваша логика инициализации страницы
        };

        // Инициализация страницы с проверкой авторизации
        Auth.initAuthenticatedPage();
    </script>
</body>
</html>
```

### Обновление информации о пользователе

Компонент автоматически обновляет информацию о пользователе во всех элементах навигации:

```javascript
// Обновление данных пользователя
window.NavigationComponent.updateUserInfo(user);
```

### Выделение активной страницы

Компонент автоматически выделяет активную страницу в навигации на основе текущего URL.

## API компонента

### Глобальные функции

- `showNotifications()` - Показать уведомления
- `showMessages()` - Показать сообщения  
- `logout()` - Выход из системы
- `toggleUserDropdown()` - Переключение dropdown пользователя
- `toggleMobileMenu()` - Переключение мобильного меню
- `toggleSidebar()` - Переключение боковой навигации

### NavigationComponent объект

- `NavigationComponent.setActivePage()` - Установить активную страницу
- `NavigationComponent.syncUserData()` - Синхронизировать данные пользователя
- `NavigationComponent.updateUserInfo(user)` - Обновить информацию о пользователе

## События

### navigationLoaded

Событие срабатывает после успешной загрузки навигации:

```javascript
document.addEventListener('navigationLoaded', function() {
    console.log('Навигация загружена');
    // Ваша логика после загрузки навигации
});
```

## Структура навигации

### Основные разделы

- 🏠 Главная (`/dashboard/main.html`)
- 📋 Задачи (`/dashboard/tasks.html`)
- 📅 Встречи (`/dashboard/meetings.html`)
- 🛒 Покупки (`/dashboard/shopping.html`)
- 📝 Заметки (`/dashboard/notes.html`)
- ⚙️ Настройки (`/dashboard/settings.html`)
- 🎨 UI Kit (`/dashboard/ui-kit.html`)

### Добавление нового раздела

Чтобы добавить новый раздел в навигацию, отредактируйте файл `navigation-component.html`:

1. В боковой навигации (`.navigation-demo`):
```html
<a href="/dashboard/new-page.html" class="nav-item" data-page="new-page">
    <span>🆕</span>
    Новый раздел
</a>
```

2. В мобильном меню (`#mobile-menu-dropdown`):
```html
<a href="/dashboard/new-page.html" class="navbar-dropdown-item">
    <span class="navbar-dropdown-item-icon">🆕</span>
    Новый раздел
</a>
```

## Стилизация

Компонент использует CSS переменные из `dashboard-styles.css` и `navigation.css`. Основные классы:

- `.navbar` - Верхняя навигация
- `.sidebar` - Боковая навигация
- `.nav-item` - Элемент навигации
- `.nav-item.active` - Активный элемент навигации
- `.navbar-dropdown` - Выпадающее меню
- `.mobile-menu-btn` - Кнопка мобильного меню

## Совместимость

Компонент совместим с:
- Системой авторизации (`auth.js`)
- Существующими стилями дашборда
- Мобильными устройствами
- Всеми современными браузерами

## Миграция существующих страниц

1. Удалите существующую навигацию из HTML
2. Добавьте `<script src="navigation-loader.js"></script>`
3. Оберните основной контент в подходящий контейнер
4. Обновите callback функции для работы с пользователем

## Пример миграции

### До:
```html
<body>
    <nav class="navbar">...</nav>
    <div class="sidebar">...</div>
    <div class="main-content">
        <div class="content">...</div>
    </div>
</body>
```

### После:
```html
<body>
    <!-- Навигация будет загружена автоматически -->
    
    <div class="content">...</div>
    
    <script src="navigation-loader.js"></script>
</body>
```

## Отладка

Для отладки компонента используйте консоль браузера:

```javascript
// Проверка загрузки компонента
console.log('NavigationComponent:', window.NavigationComponent);

// Проверка состояния навигации
console.log('Navbar:', document.querySelector('.navbar'));
console.log('Sidebar:', document.querySelector('.sidebar'));
```

## Fallback

В случае ошибки загрузки компонента автоматически показывается упрощенная навигация с основными ссылками.

## Устранение неполадок

Если навигация не отображается корректно, см. [Руководство по устранению неполадок](./NAVIGATION_TROUBLESHOOTING.md).

## Тестирование

Для тестирования компонента используйте специальную страницу `test-navigation.html`, которая показывает отладочную информацию и статус всех элементов навигации.