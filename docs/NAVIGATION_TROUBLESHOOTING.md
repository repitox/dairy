# Устранение неполадок с навигацией

## Проблема: Информация о пользователе не синхронизируется

### Симптомы:
- На одной странице отображается правильное имя пользователя (например, "Иван")
- На другой странице показывается "Пользователь" вместо реального имени
- Данные пользователя не обновляются в навигации

### Возможные причины и решения:

#### 1. Навигационный компонент загружается после обновления пользователя
**Решение:** Используйте событие `navigationLoaded`
```javascript
document.addEventListener('navigationLoaded', function() {
    const user = Auth.getCurrentUser();
    if (user && window.NavigationComponent) {
        window.NavigationComponent.updateUserInfo(user);
    }
});
```

#### 2. Функция updateUserInfo вызывается до готовности компонента
**Решение:** Добавьте fallback механизм
```javascript
function updateUserInfo(user) {
    if (window.NavigationComponent && window.NavigationComponent.updateUserInfo) {
        window.NavigationComponent.updateUserInfo(user);
    } else {
        setTimeout(() => updateUserInfo(user), 100);
    }
}
```

#### 3. Проверка синхронизации
Используйте тестовую страницу `test-user-sync.html` для диагностики проблем с синхронизацией пользователя.

## Проблема: Боковая навигация не отображается

### Возможные причины и решения:

#### 1. Кэширование браузера
**Симптомы:** Старая версия страницы загружается без изменений

**Решение:**
- Очистите кэш браузера (Ctrl+Shift+R или Cmd+Shift+R)
- Откройте инструменты разработчика (F12)
- Во вкладке Network поставьте галочку "Disable cache"
- Перезагрузите страницу

#### 2. Ошибка загрузки компонента
**Симптомы:** В консоли браузера ошибка 404 для navigation-component.html

**Проверка:**
```javascript
// В консоли браузера:
console.log('NavigationComponent:', window.NavigationComponent);
console.log('Sidebar:', document.querySelector('.sidebar'));
```

**Решение:**
- Убедитесь, что файл `navigation-component.html` существует
- Проверьте правильность пути к файлу
- Убедитесь, что сервер запущен

#### 3. JavaScript ошибки
**Симптомы:** Компонент не загружается, ошибки в консоли

**Проверка:**
- Откройте консоль разработчика (F12)
- Посмотрите на ошибки в красном цвете
- Проверьте вкладку Network на наличие неудачных запросов

#### 4. CSS стили не применяются
**Симптомы:** Sidebar есть в DOM, но не виден

**Проверка:**
```javascript
// В консоли браузера:
const sidebar = document.querySelector('.sidebar');
console.log('Sidebar styles:', window.getComputedStyle(sidebar));
```

**Решение:**
- Убедитесь, что подключен `navigation.css`
- Проверьте, что нет конфликтующих CSS правил

#### 5. Мобильная версия
**Симптомы:** На мобильных устройствах sidebar не виден

**Это нормально!** На мобильных устройствах (ширина экрана < 768px) sidebar скрыт по умолчанию.

**Как открыть:**
- Нажмите на кнопку гамбургер-меню (☰) в правом верхнем углу
- Или используйте функцию `toggleSidebar()` в консоли

## Отладочные команды

### Проверка состояния навигации:
```javascript
// Проверка загрузки компонента
console.log('NavigationComponent:', window.NavigationComponent);

// Проверка элементов DOM
console.log('Navbar:', document.querySelector('.navbar'));
console.log('Sidebar:', document.querySelector('.sidebar'));
console.log('Sidebar header:', document.querySelector('.sidebar-header'));

// Проверка функций
console.log('Functions available:', {
    showNotifications: typeof showNotifications,
    toggleSidebar: typeof toggleSidebar,
    updateUserInfo: typeof updateUserInfo
});
```

### Принудительная загрузка навигации:
```javascript
// Если навигация не загрузилась автоматически
if (window.NavigationLoader) {
    window.NavigationLoader.loadNavigation();
}
```

### Проверка пользователя:
```javascript
// Проверка текущего пользователя
const user = Auth.getCurrentUser();
console.log('Current user:', user);

// Принудительное обновление информации о пользователе
if (user && window.NavigationComponent) {
    window.NavigationComponent.updateUserInfo(user);
}
```

## Тестовая страница

Создана специальная страница для тестирования: `test-navigation.html`

Она показывает:
- Статус загрузки всех компонентов
- Отладочную информацию
- Проверку всех элементов навигации

## Частые проблемы

### 1. "NavigationComponent is undefined"
**Причина:** Компонент не загрузился или загружается асинхронно

**Решение:**
```javascript
// Дождитесь события navigationLoaded
document.addEventListener('navigationLoaded', function() {
    // Теперь NavigationComponent доступен
    console.log('Navigation ready!');
});
```

### 2. Контент страницы не перемещается в sidebar
**Причина:** Функция `wrapPageContent` не находит контент

**Решение:**
- Убедитесь, что контент не находится внутри навигационных элементов
- Проверьте, что элемент с id="page-content" создался

### 3. Стили навигации конфликтуют со стилями страницы
**Решение:**
- Используйте более специфичные селекторы
- Проверьте порядок подключения CSS файлов
- Используйте `!important` только в крайних случаях

## Если ничего не помогает

1. Откройте `test-navigation.html` в браузере
2. Проверьте отладочную информацию на странице
3. Скопируйте все ошибки из консоли
4. Проверьте, что все файлы существуют:
   - `navigation-component.html`
   - `navigation-loader.js`
   - `navigation.css`
   - `dashboard-styles.css`

## Fallback режим

Если компонент навигации не загружается, автоматически показывается упрощенная навигация с основными ссылками. Это означает, что проблема в загрузке основного компонента.