# 🔒 Безопасность проекта

## ⚠️ ВАЖНО: Файлы, которые НЕ должны попасть в Git

### 🚫 **Никогда не коммитьте:**

```bash
# Файлы с секретными данными
.env                    # Реальные токены и пароли
.env.local             # Локальные настройки
.env.docker            # Docker переменные окружения
.env.production        # Продакшен настройки

# Базы данных
*.db                   # SQLite базы
*.sqlite*              # SQLite файлы
*.sql                  # Дампы базы данных

# Логи
logs/                  # Папка с логами
*.log                  # Файлы логов

# Docker данные
postgres_data/         # Данные PostgreSQL
```

### ✅ **Можно коммитить:**

```bash
.env.example          # Шаблон настроек (без секретов)
.gitignore           # Правила игнорирования
docker-compose.yml   # Конфигурация Docker
Dockerfile          # Образ приложения
README.md           # Документация
```

## 🔐 **Настройка переменных окружения**

### Для разработки:
```bash
# 1. Скопируйте шаблон
cp .env.example .env

# 2. Отредактируйте .env файл
nano .env

# 3. Добавьте реальные значения:
BOT_TOKEN=7105955108:AAHf4cICJWShQfoixAfvVBt_5a3KleCJw_Q
DOMAIN=http://localhost:8000
VERIFY_TELEGRAM_SIGNATURE=false
```

### Для продакшена:
```bash
# Используйте переменные окружения сервера
export BOT_TOKEN="your_real_token"
export DOMAIN="https://yourdomain.com"
export VERIFY_TELEGRAM_SIGNATURE="true"
export DATABASE_URL="postgresql://user:pass@host:5432/db"
```

## 🛡️ **Уровни безопасности**

### 🔧 **Разработка (localhost)**
```env
VERIFY_TELEGRAM_SIGNATURE=false  # Отключена проверка
LOCAL_DEV_MODE=true             # Включена локальная авторизация
DOMAIN=http://localhost:8000    # Локальный домен
```

### 🚀 **Продакшен (сервер)**
```env
VERIFY_TELEGRAM_SIGNATURE=true  # Включена проверка подписи
LOCAL_DEV_MODE=false           # Отключена локальная авторизация
DOMAIN=https://yourdomain.com  # HTTPS обязательно
```

## 🔍 **Проверка безопасности**

### Перед коммитом:
```bash
# Проверьте, что секретные файлы не добавлены
git status

# Убедитесь, что .env файлы игнорируются
git check-ignore .env .env.docker

# Проверьте содержимое коммита
git diff --cached
```

### Если случайно добавили секреты:
```bash
# Удалите файл из индекса (но оставьте локально)
git rm --cached .env

# Добавьте в .gitignore если еще не добавлено
echo ".env" >> .gitignore

# Если уже закоммитили - используйте git filter-branch
# или создайте новый репозиторий
```

## 🚨 **Что делать при утечке токена**

### 1. Немедленно:
- Отзовите токен в @BotFather
- Создайте новый токен
- Обновите переменные окружения

### 2. В @BotFather:
```
/revoke - отозвать токен
/newtoken - создать новый
```

### 3. Обновите настройки:
```bash
# Обновите .env файл с новым токеном
BOT_TOKEN=new_token_here

# Перезапустите приложение
docker-compose restart app
```

## 📋 **Чеклист безопасности**

### ✅ Перед деплоем:
- [ ] `.env` файлы добавлены в `.gitignore`
- [ ] Используется HTTPS для продакшена
- [ ] Включена проверка подписи Telegram
- [ ] Отключена локальная авторизация
- [ ] Сложные пароли для базы данных
- [ ] Логи не содержат секретной информации

### ✅ Регулярно:
- [ ] Обновляйте зависимости
- [ ] Проверяйте логи на подозрительную активность
- [ ] Делайте бэкапы базы данных
- [ ] Мониторьте использование API

## 🔗 **Полезные ссылки**

- [Telegram Bot Security](https://core.telegram.org/bots#security)
- [OWASP Security Guidelines](https://owasp.org/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)

---

## ⚡ **Быстрая настройка для нового разработчика**

```bash
# 1. Клонируйте репозиторий
git clone <repository-url>
cd tg_project

# 2. Скопируйте настройки
cp .env.example .env

# 3. Получите токен бота у администратора
# (НЕ используйте продакшен токен для разработки!)

# 4. Запустите Docker
./docker-start.sh

# 5. Откройте http://localhost:8000/local-auth
```

**Готово! Можете разрабатывать безопасно.** 🚀