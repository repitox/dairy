# 🔧 Руководство по локальной разработке

## 🚀 Быстрый старт для разработки

### 1. Запуск приложения
```bash
./docker-start.sh
```

### 2. Откройте в браузере
**Главная страница:** http://localhost:8000/dashboard/

На localhost автоматически активируется **режим локальной разработки** - вместо Telegram Login Widget появится кнопка "Войти как тестовый пользователь".

### 3. Локальная авторизация
**Прямая ссылка:** http://localhost:8000/local-auth

Выберите одного из тестовых пользователей:
- **Иван Разработчик** (ID: 123456789)
- **Мария Тестер** (ID: 987654321) 
- **Админ Системы** (ID: 555666777)

## 🔄 Как это работает

### Автоматическое определение режима
```javascript
// В dashboard/index.html
const isLocalhost = window.location.hostname === 'localhost';
if (isLocalhost) {
    // Показываем кнопку локальной авторизации
    // Скрываем Telegram Login Widget
}
```

### Эмуляция авторизации
```javascript
// В local_auth.html
const fakeUserData = {
    id: userId,
    first_name: firstName,
    username: username,
    hash: "fake_hash_for_local_dev"
};

// Отправляем на тот же API endpoint
fetch('/api/auth/telegram', {
    method: 'POST',
    body: JSON.stringify(fakeUserData)
})
```

### Отключение проверки подписи
```env
# В .env.docker
VERIFY_TELEGRAM_SIGNATURE=false
```

## 🌐 Доступные URL для разработки

- **🔧 Локальная авторизация:** http://localhost:8000/local-auth
- **🏠 Главная страница:** http://localhost:8000/dashboard/
- **📱 Тест Telegram авторизации:** http://localhost:8000/test-auth
- **⚡ WebApp:** http://localhost:8000/webapp/
- **🗄️ Adminer (БД):** http://localhost:8080

## 🔄 Переключение между режимами

### Локальная разработка (localhost)
- ✅ Автоматически активируется на localhost
- ✅ Эмуляция авторизации через тестовых пользователей
- ✅ Отключена проверка подписи Telegram
- ✅ Не требует настройки домена в @BotFather

### Продакшен (домен)
- ✅ Настоящий Telegram Login Widget
- ✅ Проверка подписи включена
- ✅ Требует настройки домена в @BotFather

## 🧪 Тестирование функций

### Создание задач
```javascript
// Пример API запроса
fetch('/api/tasks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        user_id: 123456789,
        project_id: 1,
        title: "Тестовая задача",
        description: "Описание задачи"
    })
})
```

### Создание событий
```javascript
fetch('/api/events', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        user_id: 123456789,
        project_id: 1,
        title: "Тестовое событие",
        location: "Офис",
        start_at: "2024-01-01T10:00:00",
        end_at: "2024-01-01T11:00:00"
    })
})
```

## 🗄️ Работа с базой данных

### Подключение через Adminer
1. Откройте http://localhost:8080
2. Введите данные:
   - **Система:** PostgreSQL
   - **Сервер:** db
   - **Пользователь:** postgres
   - **Пароль:** password
   - **База данных:** telegram_app

### Подключение через командную строку
```bash
# Подключение к БД
docker-compose exec db psql -U postgres -d telegram_app

# Просмотр таблиц
\dt

# Просмотр пользователей
SELECT * FROM users;
```

## 🔧 Отладка

### Просмотр логов
```bash
# Все логи
docker-compose logs -f

# Только приложение
docker-compose logs -f app

# Только база данных
docker-compose logs -f db
```

### Перезапуск сервисов
```bash
# Перезапуск приложения
docker-compose restart app

# Полный перезапуск
docker-compose down && docker-compose up -d
```

## 🚨 Важные моменты

### ⚠️ Только для разработки!
- Локальная авторизация работает **только на localhost**
- В продакшене используется настоящая Telegram авторизация
- Не используйте тестовых пользователей в продакшене

### 🔒 Безопасность
- Проверка подписи отключена только для localhost
- В продакшене всегда включайте `VERIFY_TELEGRAM_SIGNATURE=true`
- Используйте HTTPS для продакшена

### 📱 Telegram бот
- Бот работает независимо от веб-авторизации
- Для тестирования бота используйте настоящий Telegram
- Команды: `/start`, `/test_notify`

## 🎯 Готово!

Теперь вы можете разрабатывать локально без необходимости:
- ✅ Настраивать домен в @BotFather каждый раз
- ✅ Использовать настоящий Telegram для авторизации
- ✅ Беспокоиться о проверке подписи

**Просто откройте http://localhost:8000/dashboard/ и начинайте разработку!** 🚀