# Telegram Bot Project

Телеграм бот для управления задачами с интеграцией в систему Dialist.

## Стек технологий

**Телеграм бот:**
- Python + FastAPI
- БД: внешнее подключение к БД проекта Dialist

**Проект Dialist:**
- Бекенд: PHP + Laravel
- БД: PostgreSQL
- Фронтенд: React

## Быстрый старт

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Настройте переменные окружения:
```bash
cp .env.example .env
# Отредактируйте .env файл
```

3. Запустите бота:
```bash
python bot.py
```

## Документация

Вся подробная документация находится в папке [`docs/`](./docs/).

📚 **[Полный индекс документации](./docs/INDEX.md)**

### Основная документация
- [📋 Инструкции по настройке](./docs/SETUP.md)
- [🚀 Инструкции по деплою](./docs/DEPLOY_INSTRUCTIONS.md)
- [🔧 Локальная разработка](./docs/LOCAL_DEV_GUIDE.md)
- [🐳 Docker](./docs/DOCKER_README.md)

### Система аутентификации
- [🔐 Система аутентификации](./docs/AUTH_SYSTEM.md)
- [📱 Настройка Telegram Auth](./docs/TELEGRAM_AUTH_SETUP.md)

### UI и дизайн
- [🎨 UI Kit Guide](./docs/UI_KIT_GUIDE.md)
- [📊 Отчет о миграции UI Kit](./docs/UI_KIT_MIGRATION_REPORT.md)
- [🌈 Система тем](./docs/THEME_SYSTEM.md)
- [✨ Glassmorphism эффекты](./docs/GLASSMORPHISM_REPORT.md)
- [📱 Мобильная адаптация UI Kit](./docs/MOBILE_ADAPTATION_REPORT.md)
- [📋 Руководство по мобильным классам](./docs/MOBILE_CLASSES_GUIDE.md)
- [🧭 Использование навигационной панели](./docs/NAVBAR_USAGE.md)
- [🧭 Компонент навигации](./docs/NAVIGATION_COMPONENT.md)
- [🔧 Улучшения верстки WebApp](./docs/WEBAPP_LAYOUT_IMPROVEMENTS.md)
- [🔄 Ревизия CSS и добавление страницы задач](./docs/WEBAPP_CSS_REVISION.md)

### Функциональность
- [📝 Раздел "Заметки"](./docs/NOTES_FEATURE.md)

### Отчеты об обновлениях
- [📝 Changelog](./docs/CHANGELOG.md)
- [✅ Завершение миграции навигации](./docs/NAVIGATION_MIGRATION_COMPLETE.md)
- [🔄 Рефакторинг навигации Dashboard](./docs/NAVIGATION_REFACTORING_REPORT.md)
- [🔄 Обновления навигации дашборда](./docs/DASHBOARD_NAVIGATION_UPDATE.md)
- [🧭 Обновление боковой навигации](./docs/SIDEBAR_NAVIGATION_UPDATE.md)
- [📋 Обновления страницы задач](./docs/TASKS_PAGE_UPDATE.md)
- [🏠 Обновление главной страницы дашборда](./docs/DASHBOARD_MAIN_UPDATE.md)

### Безопасность
- [🔒 Безопасность](./docs/SECURITY.md)
- [✅ Чеклист безопасности Git](./docs/GIT_SAFETY_CHECKLIST.md)

## Основные функции

### Dashboard (Веб-интерфейс)
- 📋 **Задачи** - Управление задачами с проектами и приоритетами
- 📅 **Встречи** - Планирование и управление событиями
- 🛒 **Покупки** - Список покупок с отметками выполнения
- 📝 **Заметки** - Создание и редактирование заметок с Markdown поддержкой
- ⚙️ **Настройки** - Персонализация и конфигурация

### Telegram WebApp
- Мобильный интерфейс для работы через Telegram
- Синхронизация с веб-дашбордом
- Push-уведомления

## Структура проекта

```
├── bot.py              # Основной файл бота
├── dashboard/          # Веб-интерфейс дашборда
│   ├── notes.html      # Список заметок
│   ├── note-create.html # Создание/редактирование заметки
│   └── note-view.html  # Просмотр заметки
├── static/             # Статические файлы WebApp
├── docs/              # Документация
│   └── NOTES_FEATURE.md # Документация раздела заметок
├── requirements.txt    # Python зависимости
└── docker-compose.yml  # Docker конфигурация
```

## Разработка

Для локальной разработки см. [LOCAL_DEV_GUIDE.md](./docs/LOCAL_DEV_GUIDE.md)

## Лицензия

Проект разрабатывается для внутреннего использования.