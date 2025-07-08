# 🚀 Первоначальная настройка проекта

## 📋 **Для нового разработчика**

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd tg_project
```

### 2. Настройка переменных окружения
```bash
# Скопируйте шаблон настроек
cp .env.example .env

# Отредактируйте файл .env
nano .env
```

**Минимальные настройки для разработки:**
```env
BOT_TOKEN=your_bot_token_here
DOMAIN=http://localhost:8000
VERIFY_TELEGRAM_SIGNATURE=false
DATABASE_URL=postgresql://postgres:password@localhost:5432/telegram_app
```

### 3. Получение токена бота

#### Создание нового бота (если нужно):
1. Откройте [@BotFather](https://t.me/BotFather)
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Скопируйте токен в `.env` файл

#### Использование существующего бота:
- Попросите токен у администратора проекта
- **НЕ используйте продакшен токен для разработки!**

### 4. Запуск проекта

#### Вариант A: Docker (рекомендуется)
```bash
# Установите Docker Desktop
# https://www.docker.com/products/docker-desktop/

# Запустите проект
./docker-start.sh

# Откройте в браузере
http://localhost:8000/local-auth
```

#### Вариант B: Локальная установка
```bash
# Установите зависимости
pip3 install -r requirements.txt

# Установите PostgreSQL
# macOS: brew install postgresql
# Ubuntu: sudo apt install postgresql

# Создайте базу данных
createdb telegram_app

# Запустите сервер
python3 start_server.py
```

## 🔧 **Настройка IDE**

### Visual Studio Code
Рекомендуемые расширения:
- Python
- Docker
- PostgreSQL
- GitLens

### Настройки проекта (.vscode/settings.json):
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".env": true
    }
}
```

## 🗄️ **Настройка базы данных**

### Docker (автоматически)
База данных настраивается автоматически при запуске `./docker-start.sh`

### Локальная PostgreSQL
```bash
# Создание пользователя и базы
sudo -u postgres psql
CREATE USER telegram_user WITH PASSWORD 'password';
CREATE DATABASE telegram_app OWNER telegram_user;
GRANT ALL PRIVILEGES ON DATABASE telegram_app TO telegram_user;
\q

# Обновите DATABASE_URL в .env
DATABASE_URL=postgresql://telegram_user:password@localhost:5432/telegram_app
```

## 🤖 **Настройка Telegram бота**

### Для локальной разработки:
**Ничего настраивать не нужно!** Используйте локальную авторизацию.

### Для продакшена:
1. Откройте [@BotFather](https://t.me/BotFather)
2. Отправьте `/setdomain`
3. Выберите вашего бота
4. Введите домен: `https://yourdomain.com`

### Дополнительные команды бота:
```bash
# Установка описания
/setdescription
Система управления задачами и событиями

# Установка команд
/setcommands
start - Запуск бота
test_notify - Тест уведомлений
```

## 🧪 **Тестирование**

### Проверка работоспособности:
```bash
# Проверка API
curl http://localhost:8000/ping

# Проверка авторизации
curl -X POST http://localhost:8000/api/auth/telegram \
  -H "Content-Type: application/json" \
  -d '{"id": 123456789, "first_name": "Test", "hash": "test"}'

# Проверка базы данных
docker-compose exec db psql -U postgres -d telegram_app -c "SELECT * FROM users;"
```

### Тестовые пользователи:
- **Иван Разработчик** (ID: 123456789, @ivan_dev)
- **Мария Тестер** (ID: 987654321, @maria_test)
- **Админ Системы** (ID: 555666777, @admin_user)

## 🚨 **Устранение проблем**

### Проблема: Docker не запускается
```bash
# Проверьте статус Docker
docker --version
docker-compose --version

# Перезапустите Docker Desktop
# Очистите кэш
docker system prune -a
```

### Проблема: База данных недоступна
```bash
# Проверьте логи
docker-compose logs db

# Перезапустите базу
docker-compose restart db

# Проверьте подключение
docker-compose exec app python -c "from db import get_conn; print('OK' if get_conn() else 'Error')"
```

### Проблема: Порт занят
```bash
# Найдите процесс
lsof -i :8000

# Остановите процесс
kill -9 <PID>

# Или измените порт в docker-compose.yml
```

### Проблема: Авторизация не работает
1. Проверьте, что используете http://localhost:8000
2. Откройте консоль браузера (F12)
3. Проверьте логи: `docker-compose logs app`
4. Убедитесь, что `VERIFY_TELEGRAM_SIGNATURE=false`

## 📚 **Полезные команды**

### Git
```bash
# Проверка статуса
git status

# Проверка игнорируемых файлов
git check-ignore .env .env.docker

# Коммит изменений
git add .
git commit -m "feat: добавил новую функцию"
git push
```

### Docker
```bash
# Просмотр логов
./docker-logs.sh

# Перезапуск
docker-compose restart app

# Остановка
./docker-stop.sh

# Подключение к контейнеру
docker-compose exec app bash
```

### База данных
```bash
# Подключение к БД
docker-compose exec db psql -U postgres -d telegram_app

# Бэкап
docker-compose exec db pg_dump -U postgres telegram_app > backup.sql

# Восстановление
docker-compose exec -T db psql -U postgres telegram_app < backup.sql
```

## ✅ **Чеклист готовности**

Перед началом разработки убедитесь:

- [ ] Репозиторий склонирован
- [ ] `.env` файл создан и настроен
- [ ] Docker Desktop установлен и запущен
- [ ] `./docker-start.sh` выполнен успешно
- [ ] http://localhost:8000/local-auth открывается
- [ ] Авторизация работает
- [ ] База данных доступна через Adminer
- [ ] Логи не содержат ошибок

## 🎯 **Готово!**

Теперь вы можете:
- 🔧 Разрабатывать локально без настройки Telegram
- 🗄️ Работать с базой данных через Adminer
- 📱 Тестировать API endpoints
- 🚀 Деплоить на продакшен

**Удачной разработки!** 🚀