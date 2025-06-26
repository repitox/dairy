# 🚀 Telegram App - Система управления задачами

Полнофункциональное веб-приложение с авторизацией через Telegram, управлением задачами, событиями и покупками.

## ✨ Возможности

- 🔐 **Авторизация через Telegram** - безопасный вход через Telegram Login Widget
- 📋 **Управление задачами** - создание, редактирование, отслеживание задач
- 📅 **События и мероприятия** - планирование и напоминания
- 🛒 **Список покупок** - совместное ведение списков покупок
- 👥 **Проекты** - организация работы по проектам
- 🤖 **Telegram бот** - уведомления и взаимодействие через бота
- 📱 **WebApp** - мобильная версия для Telegram

## 🚀 Быстрый старт

### Вариант 1: Docker (Рекомендуется)

```bash
# 1. Установите Docker Desktop
# https://www.docker.com/products/docker-desktop/

# 2. Запустите приложение
./docker-start.sh

# 3. Откройте в браузере
# http://localhost:8000/test-auth
```

### Вариант 2: Локальная установка

```bash
# 1. Установите зависимости
pip3 install -r requirements.txt

# 2. Настройте переменные окружения
cp .env.example .env
# Отредактируйте .env файл

# 3. Запустите сервер
python3 start_server.py
```

## ⚙️ Настройка Telegram бота

**ВАЖНО:** Для работы авторизации нужно настроить домен в @BotFather:

1. Откройте чат с [@BotFather](https://t.me/BotFather)
2. Отправьте команду `/setdomain`
3. Выберите бота `@rptx_bot`
4. Отправьте домен: `https://rptx.na4u.ru` (или ваш домен)

```bash
# Получить информацию о боте
python3 get_bot_info.py

# Инструкции по настройке
python3 setup_bot.py
```

## 🌐 Доступные URL

После запуска приложения:

- **Тест авторизации:** http://localhost:8000/test-auth
- **Главная страница:** http://localhost:8000/dashboard/
- **WebApp:** http://localhost:8000/webapp/
- **Adminer (БД):** http://localhost:8080 _(только в Docker)_

## 🏗️ Архитектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│                 │    │                 │    │                 │
│ • Dashboard     │◄──►│ • FastAPI       │◄──►│ • PostgreSQL    │
│ • WebApp        │    │ • Telegram Bot  │    │ • Tables        │
│ • Auth Pages    │    │ • API Endpoints │    │ • Indexes       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Структура проекта

```
├── 🤖 Бэкенд
│   ├── bot.py                 # Основное FastAPI приложение
│   ├── db.py                  # Работа с базой данных
│   └── scheduler.py           # Планировщик задач
│
├── 🌐 Фронтенд
│   ├── dashboard/             # Веб-интерфейс
│   │   ├── index.html         # Страница авторизации
│   │   └── main.html          # Главная страница
│   ├── static/                # WebApp файлы
│   └── test_auth.html         # Тестирование авторизации
│
├── 🐳 Docker
│   ├── Dockerfile             # Образ приложения
│   ├── docker-compose.yml     # Конфигурация сервисов
│   ├── docker-start.sh        # Скрипт запуска
│   └── docker-stop.sh         # Скрипт остановки
│
├── 🔧 Утилиты
│   ├── get_bot_info.py        # Информация о боте
│   ├── setup_bot.py           # Настройка бота
│   └── start_server.py        # Запуск сервера
│
└── 📚 Документация
    ├── README.md              # Этот файл
    ├── DOCKER_README.md       # Docker инструкции
    └── TELEGRAM_AUTH_SETUP.md # Настройка авторизации
```

## 🔐 Безопасность

### Авторизация через Telegram
- ✅ Официальный Telegram Login Widget
- ✅ HMAC-SHA256 проверка подписи
- ✅ Валидация данных пользователя
- ✅ Безопасное хранение сессий

### Настройки безопасности
```env
# Включить проверку подписи (продакшен)
VERIFY_TELEGRAM_SIGNATURE=true

# Использовать HTTPS
DOMAIN=https://yourdomain.com
```

## 🗄️ База данных

### Таблицы
- `users` - Пользователи
- `projects` - Проекты
- `tasks` - Задачи
- `events` - События
- `shopping` - Покупки
- `logs` - Логи системы
- `user_settings` - Настройки пользователей

### Подключение
```bash
# Docker
docker-compose exec db psql -U postgres -d telegram_app

# Локально (если PostgreSQL установлен)
psql postgresql://postgres:password@localhost:5432/telegram_app
```

## 🔧 API Endpoints

### Авторизация
- `POST /api/auth/telegram` - Авторизация через Telegram

### Задачи
- `GET /api/tasks` - Получить задачи
- `POST /api/tasks` - Создать задачу
- `PUT /api/tasks/{id}` - Обновить задачу
- `DELETE /api/tasks/{id}` - Удалить задачу

### События
- `GET /api/events` - Получить события
- `POST /api/events` - Создать событие
- `PUT /api/events/{id}` - Обновить событие

### Покупки
- `GET /api/shopping` - Получить покупки
- `POST /api/shopping` - Добавить покупку
- `PUT /api/shopping/{id}` - Обновить статус

## 🛠️ Разработка

### Локальная разработка
```bash
# Запуск с автоперезагрузкой
python3 start_server.py

# Просмотр логов
tail -f logs/app.log
```

### Docker разработка
```bash
# Запуск в режиме разработки
./docker-start.sh

# Просмотр логов
./docker-logs.sh

# Перезапуск сервиса
docker-compose restart app
```

## 🚨 Устранение неполадок

### Проблемы с авторизацией
1. Убедитесь, что домен настроен в @BotFather
2. Проверьте правильность BOT_TOKEN
3. Протестируйте на `/test-auth`

### Проблемы с базой данных
1. Проверьте DATABASE_URL
2. Убедитесь, что PostgreSQL запущен
3. Проверьте права доступа

### Проблемы с Docker
1. Убедитесь, что Docker Desktop запущен
2. Проверьте свободное место на диске
3. Перезапустите Docker

## 📊 Мониторинг

### Логи
```bash
# Все логи
docker-compose logs -f

# Логи приложения
docker-compose logs -f app

# Логи базы данных
docker-compose logs -f db
```

### Метрики
- Использование ресурсов: `docker stats`
- Размер образов: `docker images`
- Дисковое пространство: `docker system df`

## 🤝 Участие в разработке

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Протестируйте изменения
5. Создайте Pull Request

## 📝 Лицензия

MIT License - см. файл LICENSE

## 🆘 Поддержка

- 📧 Email: support@example.com
- 💬 Telegram: @support_bot
- 🐛 Issues: GitHub Issues

---

## 🎯 Готово к использованию!

1. **Установите Docker Desktop**
2. **Запустите:** `./docker-start.sh`
3. **Настройте бота в @BotFather**
4. **Откройте:** http://localhost:8000/test-auth

**Приложение готово к работе! 🚀**