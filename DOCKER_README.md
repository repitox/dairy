# 🐳 Docker Setup для Telegram App

## 🚀 Быстрый старт

### 1. Установка Docker
Убедитесь, что у вас установлен [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### 2. Запуск приложения
```bash
# Запуск всех сервисов
./docker-start.sh

# Или вручную
docker-compose up -d
```

### 3. Доступ к приложению
- **Основное приложение:** http://localhost:8000
- **Тест авторизации:** http://localhost:8000/test-auth
- **Главная страница:** http://localhost:8000/dashboard/
- **WebApp:** http://localhost:8000/webapp/
- **Adminer (БД):** http://localhost:8080

## 🏗️ Архитектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram App  │    │   PostgreSQL    │    │    Adminer      │
│   (Port 8000)   │◄──►│   (Port 5432)   │◄──►│   (Port 8080)   │
│                 │    │                 │    │                 │
│ • FastAPI       │    │ • База данных   │    │ • Веб-интерфейс │
│ • Telegram Bot  │    │ • Автобэкап     │    │   для БД        │
│ • WebApp        │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Структура Docker файлов

```
├── Dockerfile              # Образ приложения
├── docker-compose.yml      # Конфигурация сервисов
├── .dockerignore          # Исключения для Docker
├── .env.docker            # Переменные окружения для Docker
├── init.sql               # Инициализация базы данных
├── docker-start.sh        # Скрипт запуска
├── docker-stop.sh         # Скрипт остановки
└── docker-logs.sh         # Просмотр логов
```

## ⚙️ Конфигурация

### Переменные окружения (.env.docker)
```env
BOT_TOKEN=7105955108:AAHf4cICJWShQfoixAfvVBt_5a3KleCJw_Q
DOMAIN=http://localhost:8000
VERIFY_TELEGRAM_SIGNATURE=false
DATABASE_URL=postgresql://postgres:password@db:5432/telegram_app
```

### Сервисы в docker-compose.yml

#### 🤖 App (Основное приложение)
- **Порт:** 8000
- **Функции:** FastAPI, Telegram Bot, WebApp
- **Зависимости:** PostgreSQL

#### 🗄️ Database (PostgreSQL)
- **Порт:** 5432
- **База:** telegram_app
- **Пользователь:** postgres
- **Пароль:** password

#### 🌐 Adminer (Веб-интерфейс БД)
- **Порт:** 8080
- **Функции:** Управление базой данных через веб

## 🛠️ Команды управления

### Запуск
```bash
# Полный запуск с логами
./docker-start.sh

# Запуск в фоне
docker-compose up -d

# Запуск с пересборкой
docker-compose up --build -d
```

### Остановка
```bash
# Остановка всех сервисов
./docker-stop.sh

# Остановка вручную
docker-compose down

# Остановка с удалением данных
docker-compose down -v
```

### Логи
```bash
# Просмотр всех логов
./docker-logs.sh

# Логи конкретного сервиса
docker-compose logs -f app
docker-compose logs -f db
docker-compose logs -f adminer
```

### Управление
```bash
# Статус контейнеров
docker-compose ps

# Перезапуск сервиса
docker-compose restart app

# Выполнение команды в контейнере
docker-compose exec app python get_bot_info.py

# Подключение к базе данных
docker-compose exec db psql -U postgres -d telegram_app
```

## 🔧 Разработка

### Горячая перезагрузка
Код автоматически перезагружается при изменениях благодаря volume mapping:
```yaml
volumes:
  - .:/app  # Синхронизация кода
```

### Отладка
```bash
# Подключение к контейнеру
docker-compose exec app bash

# Просмотр переменных окружения
docker-compose exec app env

# Проверка подключения к БД
docker-compose exec app python -c "from db import get_conn; print('DB OK' if get_conn() else 'DB Error')"
```

## 🗄️ База данных

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
# Из контейнера приложения
docker-compose exec app psql postgresql://postgres:password@db:5432/telegram_app

# Из контейнера базы данных
docker-compose exec db psql -U postgres -d telegram_app
```

### Бэкап и восстановление
```bash
# Создание бэкапа
docker-compose exec db pg_dump -U postgres telegram_app > backup.sql

# Восстановление из бэкапа
docker-compose exec -T db psql -U postgres telegram_app < backup.sql
```

## 🚨 Устранение неполадок

### Проблема: Контейнер не запускается
```bash
# Проверьте логи
docker-compose logs app

# Пересоберите образ
docker-compose build --no-cache app
```

### Проблема: База данных недоступна
```bash
# Проверьте статус БД
docker-compose ps db

# Перезапустите БД
docker-compose restart db

# Проверьте логи БД
docker-compose logs db
```

### Проблема: Порт занят
```bash
# Найдите процесс на порту 8000
lsof -i :8000

# Или измените порт в docker-compose.yml
ports:
  - "8001:8000"  # Внешний порт 8001
```

### Проблема: Нет места на диске
```bash
# Очистка неиспользуемых образов
docker system prune -a

# Очистка volumes
docker volume prune
```

## 📊 Мониторинг

### Ресурсы контейнеров
```bash
# Использование ресурсов
docker stats

# Размер образов
docker images

# Использование дискового пространства
docker system df
```

### Здоровье приложения
```bash
# Проверка доступности
curl http://localhost:8000/test-auth

# Проверка API
curl http://localhost:8000/api/auth/telegram -X POST -H "Content-Type: application/json" -d '{}'
```

## 🔒 Безопасность

### Продакшен настройки
```env
# Включите проверку подписи
VERIFY_TELEGRAM_SIGNATURE=true

# Используйте сложные пароли
POSTGRES_PASSWORD=your_secure_password_here

# Настройте HTTPS
DOMAIN=https://yourdomain.com
```

### Сеть
По умолчанию все сервисы изолированы в Docker сети и доступны только через указанные порты.

---

## 🎯 Готово к использованию!

После запуска `./docker-start.sh` у вас будет полностью рабочее приложение с:
- ✅ Telegram авторизацией
- ✅ База данных PostgreSQL
- ✅ Веб-интерфейс управления БД
- ✅ Горячая перезагрузка кода
- ✅ Логирование и мониторинг

**Не забудьте настроить домен в @BotFather для корректной работы Telegram Login Widget!**