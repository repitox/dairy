# 🧭 Navbar Component - Верхняя навигационная панель

## 🎯 Описание

Navbar - это фиксированная верхняя навигационная панель, специально разработанная для мобильных приложений и адаптивных интерфейсов. Компонент обеспечивает быстрый доступ к основным функциям приложения.

## 📱 Особенности

### ✨ **Ключевые возможности:**
- **Фиксированное позиционирование** - всегда видна в верхней части экрана
- **Полная адаптивность** - оптимизация для всех размеров экранов
- **Glassmorphism дизайн** - полупрозрачный фон с blur эффектом
- **Встроенный поиск** - красивая строка поиска с анимацией
- **Система уведомлений** - кнопки с бейджами для счетчиков
- **Dropdown меню** - выпадающее меню пользователя
- **Touch-friendly** - оптимизация для сенсорных устройств

## 🏗️ Структура компонента

### Базовая разметка
```html
<nav class="navbar">
    <!-- Логотип/Бренд -->
    <a href="#" class="navbar-brand">
        <div class="navbar-brand-icon">📱</div>
        <span>Dashboard</span>
    </a>
    
    <!-- Центральная область (поиск) -->
    <div class="navbar-center">
        <div class="navbar-search">
            <div class="navbar-search-icon">🔍</div>
            <input type="text" class="navbar-search-input" placeholder="Поиск...">
        </div>
    </div>
    
    <!-- Действия и профиль -->
    <div class="navbar-actions">
        <button class="navbar-btn">
            🔔
            <span class="navbar-btn-badge">3</span>
        </button>
        <div class="navbar-user">
            <div class="navbar-user-avatar">И</div>
            <div class="navbar-user-info">
                <div class="navbar-user-name">Иван Петров</div>
                <div class="navbar-user-status">Онлайн</div>
            </div>
        </div>
    </div>
</nav>
```

## 🎨 CSS Классы

### Основные классы
- `.navbar` - основной контейнер навигационной панели
- `.navbar-compact` - компактная версия (высота 48px вместо 60px)

### Бренд/Логотип
- `.navbar-brand` - контейнер логотипа и названия
- `.navbar-brand-icon` - иконка бренда с градиентным фоном
- `.navbar-brand:hover` - эффект при наведении

### Поиск
- `.navbar-center` - центральная область
- `.navbar-search` - контейнер поиска
- `.navbar-search-input` - поле ввода поиска
- `.navbar-search-icon` - иконка поиска
- `.navbar-search-input:focus` - состояние фокуса

### Действия
- `.navbar-actions` - контейнер кнопок действий
- `.navbar-btn` - кнопка действия
- `.navbar-btn.active` - активная кнопка
- `.navbar-btn-badge` - бейдж с числом уведомлений

### Пользователь
- `.navbar-user` - контейнер информации о пользователе
- `.navbar-user-avatar` - аватар пользователя
- `.navbar-user-info` - информация о пользователе
- `.navbar-user-name` - имя пользователя
- `.navbar-user-status` - статус пользователя

### Dropdown меню
- `.navbar-dropdown` - выпадающее меню
- `.navbar-dropdown.show` - видимое состояние меню
- `.navbar-dropdown-item` - элемент меню
- `.navbar-dropdown-item-icon` - иконка элемента меню
- `.navbar-dropdown-divider` - разделитель в меню

## 📐 Размеры и адаптивность

### Desktop (> 768px)
- **Высота:** 60px
- **Padding:** 0 20px
- **Поиск:** максимальная ширина 400px
- **Кнопки:** 40x40px
- **Аватар:** 32x32px

### Tablet (769px - 1024px)
- **Высота:** 60px
- **Padding:** 0 20px
- **Кнопки:** минимальная высота 44px (touch-friendly)

### Mobile (≤ 768px)
- **Высота:** 56px
- **Padding:** 0 16px
- **Поиск:** максимальная ширина 200px
- **Кнопки:** 36x36px
- **Аватар:** 28x28px
- **Скрытие:** текст пользователя скрывается

### Small Mobile (≤ 480px)
- **Высота:** 56px
- **Padding:** 0 12px
- **Поиск:** максимальная ширина 150px
- **Кнопки:** 32x32px
- **Аватар:** 24x24px

## 🎯 Использование

### 1. Базовый navbar
```html
<nav class="navbar">
    <a href="/" class="navbar-brand">
        <div class="navbar-brand-icon">🏠</div>
        <span>Мое приложение</span>
    </a>
    <div class="navbar-actions">
        <button class="navbar-btn">⚙️</button>
    </div>
</nav>
```

### 2. С поиском
```html
<nav class="navbar">
    <a href="/" class="navbar-brand">
        <div class="navbar-brand-icon">📱</div>
        <span>Dashboard</span>
    </a>
    <div class="navbar-center">
        <div class="navbar-search">
            <div class="navbar-search-icon">🔍</div>
            <input type="text" class="navbar-search-input" placeholder="Поиск...">
        </div>
    </div>
    <div class="navbar-actions">
        <button class="navbar-btn">👤</button>
    </div>
</nav>
```

### 3. Полная версия с уведомлениями
```html
<nav class="navbar">
    <a href="/" class="navbar-brand">
        <div class="navbar-brand-icon">📱</div>
        <span>Dashboard</span>
    </a>
    <div class="navbar-center">
        <div class="navbar-search">
            <div class="navbar-search-icon">🔍</div>
            <input type="text" class="navbar-search-input" placeholder="Поиск...">
        </div>
    </div>
    <div class="navbar-actions">
        <button class="navbar-btn">
            🔔
            <span class="navbar-btn-badge">5</span>
        </button>
        <button class="navbar-btn active">💬</button>
        <div class="navbar-user" onclick="toggleDropdown()">
            <div class="navbar-user-avatar">И</div>
            <div class="navbar-user-info">
                <div class="navbar-user-name">Иван Петров</div>
                <div class="navbar-user-status">Онлайн</div>
            </div>
        </div>
    </div>
</nav>
```

### 4. Компактная версия
```html
<nav class="navbar navbar-compact">
    <!-- Содержимое такое же, но с уменьшенными размерами -->
</nav>
```

## ⚡ JavaScript функциональность

### Dropdown меню
```javascript
function toggleUserDropdown() {
    const dropdown = document.getElementById('user-dropdown');
    dropdown.classList.toggle('show');
}

// Закрытие при клике вне меню
document.addEventListener('click', function(event) {
    const dropdown = document.getElementById('user-dropdown');
    const userButton = event.target.closest('.navbar-user');
    
    if (!userButton && dropdown) {
        dropdown.classList.remove('show');
    }
});
```

### Поиск
```javascript
document.querySelector('.navbar-search-input').addEventListener('input', function(e) {
    const query = e.target.value;
    if (query.length > 0) {
        // Выполнить поиск
        performSearch(query);
    }
});
```

### Уведомления
```javascript
function updateNotificationBadge(count) {
    const badge = document.querySelector('.navbar-btn-badge');
    if (count > 0) {
        badge.textContent = count > 99 ? '99+' : count;
        badge.style.display = 'flex';
    } else {
        badge.style.display = 'none';
    }
}
```

## 🎨 Кастомизация

### CSS переменные
```css
:root {
    --navbar-height: 60px;
    --navbar-bg: rgba(255, 255, 255, 0.08);
    --navbar-border: rgba(255, 255, 255, 0.12);
    --navbar-blur: 20px;
    --navbar-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
}
```

### Темная тема
```css
[data-theme="dark"] {
    --navbar-bg: rgba(0, 0, 0, 0.08);
    --navbar-border: rgba(255, 255, 255, 0.08);
}
```

### Цветные варианты
```css
.navbar-blue {
    --navbar-bg: rgba(84, 169, 235, 0.1);
    --navbar-border: rgba(84, 169, 235, 0.2);
}

.navbar-purple {
    --navbar-bg: rgba(139, 92, 246, 0.1);
    --navbar-border: rgba(139, 92, 246, 0.2);
}
```

## 🔧 Интеграция

### С body отступом
```css
body {
    padding-top: 60px; /* Высота navbar */
}

@media (max-width: 768px) {
    body {
        padding-top: 56px; /* Мобильная высота */
    }
}
```

### С боковой навигацией
```css
.navbar {
    left: 250px; /* Ширина сайдбара */
}

@media (max-width: 768px) {
    .navbar {
        left: 0; /* На мобильных сайдбар скрыт */
    }
}
```

## 📱 Мобильная оптимизация

### Touch-friendly размеры
- Минимальная высота кнопок: 44px
- Увеличенные отступы для касаний
- Упрощенные анимации на слабых устройствах

### Производительность
- Уменьшенный blur на мобильных (8px вместо 20px)
- Упрощенные тени
- Отключение сложных hover эффектов

## 🧪 Тестирование

### Проверочный список
- ✅ Отображение на всех размерах экранов
- ✅ Работа dropdown меню
- ✅ Анимации поиска и кнопок
- ✅ Touch взаимодействие на мобильных
- ✅ Accessibility (клавиатурная навигация)
- ✅ Производительность на слабых устройствах

### Демо страницы
- `/dashboard/ui-kit.html` - в составе UI кита
- `/dashboard/navbar-demo.html` - отдельная демо страница

## 🚀 Примеры использования

### В мобильном приложении
```html
<!-- Простой navbar для мобильного приложения -->
<nav class="navbar navbar-compact">
    <a href="/" class="navbar-brand">
        <div class="navbar-brand-icon">📱</div>
        <span>App</span>
    </a>
    <div class="navbar-actions">
        <button class="navbar-btn">🔔</button>
        <div class="navbar-user">
            <div class="navbar-user-avatar">У</div>
        </div>
    </div>
</nav>
```

### В админ панели
```html
<!-- Полнофункциональный navbar для админки -->
<nav class="navbar">
    <a href="/admin" class="navbar-brand">
        <div class="navbar-brand-icon">⚙️</div>
        <span>Admin Panel</span>
    </a>
    <div class="navbar-center">
        <div class="navbar-search">
            <div class="navbar-search-icon">🔍</div>
            <input type="text" class="navbar-search-input" placeholder="Поиск пользователей, заказов...">
        </div>
    </div>
    <div class="navbar-actions">
        <button class="navbar-btn">
            🔔
            <span class="navbar-btn-badge">12</span>
        </button>
        <button class="navbar-btn">📊</button>
        <div class="navbar-user">
            <div class="navbar-user-avatar">А</div>
            <div class="navbar-user-info">
                <div class="navbar-user-name">Администратор</div>
                <div class="navbar-user-status">Супер пользователь</div>
            </div>
        </div>
    </div>
</nav>
```

---
*Дата создания: Декабрь 2024*
*Статус: ✅ Готово к использованию*