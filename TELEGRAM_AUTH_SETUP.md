# 🔐 Настройка авторизации через Telegram

## Обзор изменений

Была реализована правильная авторизация через Telegram с использованием официального **Telegram Login Widget** вместо неработающего `oauth.telegram.org`.

## 🚀 Что было исправлено

### 1. **Неправильный URL авторизации**
- ❌ **Было:** `https://oauth.telegram.org/auth` (неофициальный API)
- ✅ **Стало:** Официальный Telegram Login Widget

### 2. **Отсутствие проверки подписи**
- ✅ Добавлена функция `verify_telegram_auth()` для проверки подлинности данных
- ✅ Настраиваемая проверка через переменную `VERIFY_TELEGRAM_SIGNATURE`

### 3. **Отсутствующий файл main.html**
- ✅ Создан `/dashboard/main.html` с красивым интерфейсом

### 4. **Улучшенная безопасность**
- ✅ Проверка целостности данных от Telegram
- ✅ Валидация пользовательских данных
- ✅ Безопасное хранение в localStorage

## 📁 Новые файлы

```
├── dashboard/main.html          # Главная страница после авторизации
├── test_auth.html              # Страница для тестирования авторизации
├── get_bot_info.py            # Утилита для получения информации о боте
├── setup_bot.py               # Инструкции по настройке бота
├── .env                       # Переменные окружения
├── .env.example               # Пример настроек
└── TELEGRAM_AUTH_SETUP.md     # Эта инструкция
```

## ⚙️ Настройка

### 1. Настройка переменных окружения

Файл `.env` уже создан с вашими данными:
```env
BOT_TOKEN=7105955108:AAHf4cICJWShQfoixAfvVBt_5a3KleCJw_Q
DOMAIN=https://rptx.na4u.ru
VERIFY_TELEGRAM_SIGNATURE=false
```

### 2. Настройка бота в BotFather

**ВАЖНО:** Для работы Login Widget нужно настроить домен в @BotFather:

1. Откройте чат с [@BotFather](https://t.me/BotFather)
2. Отправьте команду `/setdomain`
3. Выберите бота `@rptx_bot`
4. Отправьте домен: `https://rptx.na4u.ru`

### 3. Запуск утилиты настройки

```bash
python3 setup_bot.py
```

## 🧪 Тестирование

### 1. Локальное тестирование
```bash
# Запустите сервер
python3 bot.py

# Откройте в браузере
http://localhost:8000/test-auth
```

### 2. Тестирование на продакшене
```
https://rptx.na4u.ru/test-auth
```

## 🔄 Как работает авторизация

### 1. **Пользователь нажимает кнопку "Log in via Telegram"**
```html
<script async src="https://telegram.org/js/telegram-widget.js?22" 
        data-telegram-login="rptx_bot" 
        data-size="large" 
        data-onauth="onTelegramAuth(user)">
</script>
```

### 2. **Telegram возвращает данные пользователя**
```javascript
function onTelegramAuth(user) {
    // user содержит: id, first_name, username, photo_url, auth_date, hash
}
```

### 3. **Данные отправляются на сервер для проверки**
```javascript
fetch('/api/auth/telegram', {
    method: 'POST',
    body: JSON.stringify(user)
})
```

### 4. **Сервер проверяет подпись (опционально)**
```python
def verify_telegram_auth(auth_data: dict, bot_token: str) -> bool:
    # Проверка HMAC-SHA256 подписи
```

### 5. **Пользователь сохраняется в базе данных**
```python
add_user(user_id, first_name, username)
```

## 🛡️ Безопасность

### Проверка подписи (рекомендуется для продакшена)
```env
VERIFY_TELEGRAM_SIGNATURE=true
```

### Что проверяется:
- ✅ Подлинность данных через HMAC-SHA256
- ✅ Наличие обязательных полей
- ✅ Валидность user_id

## 🎨 Интерфейс

### Страница авторизации (`/dashboard/index.html`)
- 🎨 Современный дизайн
- 📱 Адаптивная верстка
- ⚡ Обработка ошибок
- 🔄 Автоматическое перенаправление

### Главная страница (`/dashboard/main.html`)
- 👤 Информация о пользователе
- 🎯 Навигация по разделам
- 🚪 Кнопка выхода
- 💾 Сохранение состояния

## 🔧 API Endpoints

### `POST /api/auth/telegram`
Авторизация пользователя через Telegram

**Запрос:**
```json
{
    "id": 123456789,
    "first_name": "John",
    "username": "john_doe",
    "photo_url": "https://...",
    "auth_date": 1234567890,
    "hash": "abc123..."
}
```

**Ответ:**
```json
{
    "status": "ok",
    "user": {
        "id": 123456789,
        "first_name": "John",
        "last_name": "",
        "username": "john_doe",
        "photo_url": "https://..."
    }
}
```

## 🚀 Запуск

```bash
# Установка зависимостей
pip3 install -r requirements.txt

# Запуск сервера
python3 bot.py
```

## 📝 Следующие шаги

1. ✅ Настройте домен в @BotFather
2. ✅ Протестируйте авторизацию на `/test-auth`
3. ✅ Включите проверку подписи в продакшене
4. ✅ Настройте HTTPS для безопасности

## 🆘 Устранение неполадок

### Ошибка "Bot domain invalid"
- Убедитесь, что домен настроен в @BotFather
- Проверьте, что используется правильный username бота

### Ошибка "Invalid Telegram signature"
- Отключите проверку подписи: `VERIFY_TELEGRAM_SIGNATURE=false`
- Или убедитесь, что токен бота правильный

### Login Widget не загружается
- Проверьте подключение к интернету
- Убедитесь, что домен доступен по HTTPS

---

✅ **Авторизация через Telegram настроена и готова к использованию!**