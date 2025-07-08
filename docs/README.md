# 📚 Документация Telegram Bot Project

> Эта папка содержит всю документацию проекта

## 🚀 Быстрая навигация

📋 **[Полный индекс документации](./INDEX.md)** - начните отсюда!

## 📁 Структура документации

```
docs/
├── INDEX.md                    # 📚 Полный индекс всей документации
├── README.md                   # 📖 Этот файл
├── MAIN_README.md              # 📖 Старый основной README проекта
│
├── 🔧 Настройка и запуск
│   ├── SETUP.md
│   ├── DEPLOY_INSTRUCTIONS.md
│   ├── LOCAL_DEV_GUIDE.md
│   └── DOCKER_README.md
│
├── 🔐 Аутентификация
│   ├── AUTH_SYSTEM.md
│   └── TELEGRAM_AUTH_SETUP.md
│
├── 🎨 UI и дизайн
│   ├── UI_KIT_GUIDE.md
│   ├── THEME_SYSTEM.md
│   ├── GLASSMORPHISM_REPORT.md
│   ├── UI_KIT_MIGRATION_REPORT.md
│   ├── UI_KIT_FINAL_REPORT.md
│   ├── UI_KIT_IMPROVEMENTS_FINAL.md
│   ├── UI_KIT_STRUCTURE_FIXED.md
│   ├── DESIGN_UPDATE_REPORT.md
│   ├── README_THEMES.md
│   ├── UI_IMPROVEMENTS_REPORT.md
│   ├── H1_FIX_REPORT.md
│   └── DUPLICATE_COLORS_FIXED.md
│
├── 📱 Отчеты об обновлениях
│   ├── CHANGELOG.md
│   ├── DASHBOARD_NAVIGATION_UPDATE.md
│   └── TASKS_PAGE_UPDATE.md
│
└── 🔒 Безопасность
    ├── SECURITY.md
    └── GIT_SAFETY_CHECKLIST.md
```

## 🔍 Поиск по документации

```bash
# Поиск по всей документации
grep -r "ключевое_слово" docs/

# Поиск в конкретной категории
grep -r "UI Kit" docs/UI_*

# Поиск по типу файлов
find docs/ -name "*.md" -exec grep -l "поисковый_запрос" {} \;
```

## 📊 Статистика документации

- **Всего файлов:** 27 документов
- **Основные категории:** 5 разделов
- **Размер документации:** ~500KB

## 📝 Как работать с документацией

1. **Начните с [INDEX.md](./INDEX.md)** - там есть полное оглавление
2. **Для быстрого старта** - см. [SETUP.md](./SETUP.md)
3. **Для разработки** - см. [LOCAL_DEV_GUIDE.md](./LOCAL_DEV_GUIDE.md)
4. **Для деплоя** - см. [DEPLOY_INSTRUCTIONS.md](./DEPLOY_INSTRUCTIONS.md)

## 🆕 Как добавить новую документацию

1. Создайте новый .md файл в соответствующей категории
2. Добавьте ссылку в [INDEX.md](./INDEX.md)
3. Обновите этот README.md при необходимости
4. Обновите основной [README.md](../README.md) если нужно

---

⬅️ [Вернуться к основному README](../README.md)