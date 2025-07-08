# ✅ Чеклист безопасности Git

## 🚫 **НИКОГДА не коммитьте эти файлы:**

```bash
.env                    # ❌ Содержит реальные токены
.env.docker            # ❌ Docker переменные окружения  
.env.local             # ❌ Локальные настройки
.env.production        # ❌ Продакшен настройки
*.log                  # ❌ Файлы логов
*.db                   # ❌ Базы данных SQLite
*.sql                  # ❌ Дампы базы данных
postgres_data/         # ❌ Данные PostgreSQL
__pycache__/           # ❌ Python кэш
.DS_Store              # ❌ macOS системные файлы
```

## ✅ **Можно безопасно коммитить:**

```bash
.env.example           # ✅ Шаблон без секретов
.gitignore            # ✅ Правила игнорирования
docker-compose.yml    # ✅ Конфигурация Docker
Dockerfile           # ✅ Образ приложения
*.py                 # ✅ Исходный код Python
*.html               # ✅ HTML файлы
*.md                 # ✅ Документация
requirements.txt     # ✅ Зависимости Python
```

## 🔍 **Перед каждым коммитом проверьте:**

```bash
# 1. Статус репозитория
git status

# 2. Что секретные файлы игнорируются
git check-ignore .env .env.docker

# 3. Содержимое коммита
git diff --cached

# 4. Нет ли секретов в коде
grep -r "BOT_TOKEN\|password\|secret" --include="*.py" .
```

## 🚨 **Если случайно добавили секреты:**

### Файл еще не закоммичен:
```bash
# Удалите из индекса
git rm --cached .env

# Добавьте в .gitignore
echo ".env" >> .gitignore
```

### Файл уже закоммичен:
```bash
# Удалите из истории (ОПАСНО!)
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env' \
  --prune-empty --tag-name-filter cat -- --all

# Или создайте новый репозиторий
```

### Токен попал в публичный репозиторий:
1. **Немедленно** отзовите токен в @BotFather
2. Создайте новый токен
3. Обновите настройки на сервере

## 📋 **Быстрая проверка безопасности:**

```bash
# Запустите этот скрипт перед push
#!/bin/bash
echo "🔍 Проверка безопасности..."

# Проверяем секретные файлы
if git ls-files | grep -E "\.(env|log|db|sqlite)$"; then
    echo "❌ Найдены секретные файлы в репозитории!"
    exit 1
fi

# Проверяем токены в коде
if git diff --cached | grep -i "bot_token\|password\|secret\|key"; then
    echo "❌ Найдены возможные секреты в коммите!"
    exit 1
fi

echo "✅ Проверка пройдена успешно"
```

## 🎯 **Итоговый статус:**

После настройки ваш `git status` должен выглядеть так:

```bash
$ git status
On branch main
Changes to be committed:
  deleted:    .env                    # ✅ Удален из отслеживания

Untracked files:
  .gitignore                         # ✅ Добавить в коммит
  SECURITY.md                        # ✅ Добавить в коммит
  docker-compose.yml                 # ✅ Добавить в коммит
  # ... другие безопасные файлы

# .env и .env.docker НЕ должны появляться в списке!
```

## 🚀 **Готово к коммиту:**

```bash
# Добавьте безопасные файлы
git add .gitignore SECURITY.md docker-compose.yml

# Сделайте коммит
git commit -m "feat: добавил Docker и систему безопасности"

# Отправьте на сервер
git push
```

---

**Помните: лучше перестраховаться, чем потом восстанавливать безопасность!** 🔒