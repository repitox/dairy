# Использование навигационной панели (Navbar) в проекте

## Обзор

В проекте используется унифицированная навигационная панель (navbar), которая соответствует дизайну из UI Kit. Это обеспечивает единообразие интерфейса во всех разделах приложения.

## Варианты навигационной панели

В UI Kit представлены следующие варианты навигационной панели:

1. **Стандартный navbar с поиском** - полная версия с поисковой строкой
2. **Navbar без поиска** - упрощенная версия без центральной области поиска
3. **Navbar с "гамбургером"** - версия с кнопкой мобильного меню
4. **Компактный navbar** - уменьшенная версия для экономии места

## Как использовать navbar в проекте

### Вариант 1: Использование компонента navbar-component.html

Рекомендуемый способ - использовать универсальный компонент `navbar-component.html`. Этот компонент содержит актуальную версию навигационной панели и может быть включен в любую страницу.

```html
<!-- Подключение navbar компонента -->
<div id="navbar-container"></div>

<script>
    // Загрузка navbar компонента
    fetch('/dashboard/navbar-component.html')
        .then(response => response.text())
        .then(html => {
            document.getElementById('navbar-container').innerHTML = html;
            
            // Инициализация скриптов navbar после загрузки
            const script = document.createElement('script');
            script.textContent = `
                // Инициализация navbar
                document.addEventListener('DOMContentLoaded', function() {
                    // Ваш код инициализации, если необходим
                });
            `;
            document.body.appendChild(script);
        });
</script>
```

### Вариант 2: Копирование HTML-структуры

Если вам нужно внести изменения в навигационную панель для конкретной страницы, вы можете скопировать HTML-структуру из `navbar-component.html` и вставить её непосредственно в вашу страницу.

```html
<!-- Navbar (из UI Kit - вариант без поиска) -->
<nav class="navbar" id="main-navbar">
    <!-- Логотип/Бренд -->
    <a href="/dashboard/main.html" class="navbar-brand">
        <div class="navbar-brand-icon">📱</div>
        <span>Dashboard</span>
    </a>
    
    <!-- Действия и профиль -->
    <div class="navbar-actions">
        <!-- Уведомления -->
        <button class="navbar-btn" title="Уведомления" onclick="showNotifications()">
            🔔
            <span class="navbar-btn-badge" id="notifications-badge">0</span>
        </button>
        
        <!-- Сообщения -->
        <button class="navbar-btn" title="Сообщения" onclick="showMessages()">
            💬
            <span class="navbar-btn-badge" id="messages-badge">0</span>
        </button>
        
        <!-- Профиль пользователя -->
        <div class="navbar-user" onclick="toggleUserDropdown()">
            <div class="navbar-user-avatar" id="user-avatar">У</div>
            <div class="navbar-user-info">
                <div class="navbar-user-name" id="user-name">Пользователь</div>
                <div class="navbar-user-status" id="user-status">Онлайн</div>
            </div>
            <div class="navbar-dropdown" id="user-dropdown">
                <!-- Содержимое выпадающего меню -->
            </div>
        </div>
        
        <!-- Мобильное меню (при необходимости) -->
    </div>
</nav>
```

## Адаптация для мобильных устройств

Навигационная панель автоматически адаптируется для мобильных устройств. На маленьких экранах:

1. Скрываются некоторые элементы (класс `navbar-mobile-hidden`)
2. Отображаются мобильные элементы (класс `navbar-mobile-only`)
3. Меняются размеры и отступы для лучшего отображения

## Функциональность JavaScript

Для корректной работы навигационной панели необходимо подключить следующие функции JavaScript:

```javascript
// Переключение dropdown пользователя
function toggleUserDropdown() {
    const dropdown = document.getElementById('user-dropdown');
    dropdown.classList.toggle('show');
}

// Переключение мобильного меню
function toggleMobileMenu() {
    const dropdown = document.getElementById('mobile-menu-dropdown');
    const btn = document.getElementById('mobile-menu-btn');
    
    dropdown.classList.toggle('show');
    btn.classList.toggle('open');
    
    // Изменяем иконку
    if (dropdown.classList.contains('show')) {
        btn.textContent = '✕';
    } else {
        btn.textContent = '☰';
    }
}

// Функции для уведомлений и сообщений
function showNotifications() {
    // Ваш код для отображения уведомлений
}

function showMessages() {
    // Ваш код для отображения сообщений
}

// Функция выхода
function logout() {
    // Ваш код для выхода из системы
}
```

## Обновление компонента

При внесении изменений в дизайн навигационной панели, следует:

1. Обновить компонент `navbar-component.html`
2. Обновить соответствующие стили в `ui-components.css`
3. Обновить документацию при необходимости

## Примечания

- Все страницы dashboard должны использовать единую навигационную панель
- При создании новых страниц рекомендуется использовать компонент `navbar-component.html`
- Для тестирования различных вариантов навигационной панели можно обратиться к UI Kit