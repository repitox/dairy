# 📱 Руководство по мобильным классам UI Kit

## Обзор

После обновления мобильной адаптации UI Kit, все компоненты автоматически адаптируются под различные разрешения экранов. Этот документ описывает новые классы и возможности.

## 🎯 Основные принципы

### Touch-Friendly размеры
- Минимальная высота кнопок: **48px**
- Минимальная высота мелких элементов: **44px**
- Размер шрифта в формах: **16px** (предотвращает zoom на iOS)

### Адаптивные breakpoints
```css
/* Мобильные (портрет) */
@media (max-width: 480px)

/* Мобильные (ландшафт) */
@media (max-width: 768px) and (orientation: landscape)

/* Планшеты (портрет) */
@media (min-width: 481px) and (max-width: 768px)

/* Планшеты (ландшафт) */
@media (min-width: 769px) and (max-width: 1024px)

/* Десктоп */
@media (min-width: 1025px)
```

## 🛠️ Новые утилитарные классы

### Safe Area поддержка
```html
<!-- Контент с учетом Safe Area -->
<div class="safe-area-content">
    <!-- Ваш контент -->
</div>

<!-- Фиксированный заголовок -->
<header class="fixed-header">
    <!-- Заголовок -->
</header>

<!-- Фиксированный футер -->
<footer class="fixed-footer">
    <!-- Футер -->
</footer>
```

### Telegram WebApp классы
```html
<!-- Viewport для Telegram WebApp -->
<div class="tg-viewport">
    <!-- Контент с Safe Area -->
    <div class="tg-safe-area">
        <!-- Ваш контент -->
    </div>
</div>
```

## 📋 Компоненты с автоматической адаптацией

### Кнопки
```html
<!-- Обычная кнопка (автоматически 48px на мобильных) -->
<button class="btn btn-primary">Кнопка</button>

<!-- Маленькая кнопка (40px на мобильных) -->
<button class="btn btn-primary btn-small">Маленькая</button>

<!-- Большая кнопка (56px на мобильных) -->
<button class="btn btn-primary btn-large">Большая</button>

<!-- Полная ширина -->
<button class="btn btn-primary btn-full">Во всю ширину</button>
```

### Формы
```html
<div class="form-group">
    <label class="form-label">Название поля</label>
    <!-- font-size: 16px автоматически на мобильных -->
    <input type="text" class="form-control" placeholder="Введите текст">
</div>

<!-- Чекбокс (24px на touch-устройствах) -->
<label class="checkbox-label">
    <input type="checkbox" class="form-checkbox">
    <span class="checkmark"></span>
    Согласен с условиями
</label>
```

### Карточки
```html
<!-- Автоматически адаптируется: 24px → 16px → 12px padding -->
<div class="card">
    <div class="card-header">
        <h3 class="card-title">Заголовок карточки</h3>
    </div>
    <div class="card-body">
        Содержимое карточки
    </div>
</div>
```

### Списки
```html
<div class="list-container">
    <div class="list-header">
        📋 Список задач
    </div>
    <!-- Автоматически адаптируется padding -->
    <div class="list-item">
        <div class="item-content">
            <div class="item-title">Название задачи</div>
            <div class="item-meta">Дополнительная информация</div>
        </div>
        <span class="badge badge-success">Выполнено</span>
    </div>
</div>
```

### Навигация
```html
<!-- Touch-friendly размеры автоматически -->
<nav class="nav-tabs">
    <a href="#" class="nav-tab active">Активная</a>
    <a href="#" class="nav-tab">Обычная</a>
</nav>

<!-- Навигационные элементы -->
<a href="#" class="nav-item">
    <span class="nav-item-icon">📋</span>
    Задачи
</a>
```

### Фильтры
```html
<!-- На мобильных автоматически вертикальная компоновка -->
<div class="filter-bar">
    <div class="filter-buttons">
        <button class="filter-btn active">Все</button>
        <button class="filter-btn">Активные</button>
        <button class="filter-btn">Завершенные</button>
    </div>
    <div class="filter-search">
        <input type="text" placeholder="Поиск...">
    </div>
</div>
```

### Бейджи и статусы
```html
<!-- Автоматически масштабируются -->
<span class="badge badge-success">Успех</span>
<span class="badge badge-warning">Предупреждение</span>
<span class="badge badge-danger">Ошибка</span>
<span class="badge badge-info">Информация</span>

<!-- Приоритеты -->
<span class="badge priority-high">Высокий</span>
<span class="badge priority-medium">Средний</span>
<span class="badge priority-low">Низкий</span>
```

## 🎨 Glassmorphism эффекты

### Контейнеры
```html
<!-- Стандартный glass контейнер -->
<div class="glass-container">
    Контент
</div>

<!-- Легкий glass эффект -->
<div class="glass-container-light">
    Контент
</div>

<!-- Сильный glass эффект -->
<div class="glass-container-heavy">
    Контент
</div>
```

## 📊 Состояния загрузки

### Загрузка
```html
<div class="loading-container">
    <div class="loading-spinner"></div>
    <div class="loading-text">Загрузка...</div>
</div>

<!-- Скелетон -->
<div class="skeleton skeleton-card"></div>
<div class="skeleton skeleton-title"></div>
<div class="skeleton skeleton-text"></div>
```

### Пустые состояния
```html
<div class="empty-state">
    <div class="empty-state-icon">📭</div>
    <h3 class="empty-state-title">Нет данных</h3>
    <p class="empty-state-description">
        Здесь пока ничего нет. Добавьте первый элемент.
    </p>
    <div class="empty-state-action">
        <button class="btn btn-primary">Добавить</button>
    </div>
</div>
```

## 🔔 Уведомления

### Toast уведомления
```html
<div class="toast-container">
    <div class="toast toast-success show">
        <div class="toast-icon">✅</div>
        <div class="toast-content">
            <div class="toast-title">Успех!</div>
            <div class="toast-message">Операция выполнена успешно</div>
        </div>
        <button class="toast-close">×</button>
    </div>
</div>
```

## 📄 Пагинация
```html
<div class="pagination">
    <a href="#" class="pagination-item disabled">‹</a>
    <a href="#" class="pagination-item active">1</a>
    <a href="#" class="pagination-item">2</a>
    <a href="#" class="pagination-item">3</a>
    <div class="pagination-dots">...</div>
    <a href="#" class="pagination-item">10</a>
    <a href="#" class="pagination-item">›</a>
</div>
```

## 💡 Советы по использованию

### 1. Автоматическая адаптация
Большинство компонентов адаптируются автоматически. Просто используйте стандартные классы.

### 2. Touch-оптимизация
На touch-устройствах hover эффекты заменяются на active состояния.

### 3. Производительность
На мобильных устройствах blur эффекты автоматически уменьшаются для лучшей производительности.

### 4. Safe Area
Используйте `.safe-area-content` для основного контента в Telegram WebApp.

### 5. Тестирование
Всегда тестируйте на реальных устройствах, особенно в Telegram WebApp.

## 🚀 Примеры использования

### Мобильная страница задач
```html
<div class="tg-viewport">
    <div class="safe-area-content">
        <h1>📋 Мои задачи</h1>
        
        <div class="filter-bar">
            <div class="filter-buttons">
                <button class="filter-btn active">Все</button>
                <button class="filter-btn">Сегодня</button>
            </div>
            <div class="filter-search">
                <input type="text" placeholder="Поиск задач...">
            </div>
        </div>
        
        <div class="list-container">
            <div class="list-header">
                📌 Активные задачи
            </div>
            <div class="list-item">
                <div class="checkbox">
                    <input type="checkbox" class="form-checkbox">
                    <span class="checkmark"></span>
                </div>
                <div class="item-content">
                    <div class="item-title">Важная задача</div>
                    <div class="item-meta">Срок: сегодня</div>
                </div>
                <span class="badge priority-high">Высокий</span>
            </div>
        </div>
        
        <button class="btn btn-primary btn-full">
            ➕ Добавить задачу
        </button>
    </div>
</div>
```

---
*Обновлено: Декабрь 2024*
*Версия UI Kit: 2.0*