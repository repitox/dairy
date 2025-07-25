# 📝 Правила ведения CHANGELOG

## 🎯 Общие принципы

1. **Семантическое версионирование**: MAJOR.MINOR.PATCH (например, v2.1.3)
2. **Хронологический порядок**: Новые версии сверху
3. **Группировка изменений**: По типам (новые функции, исправления, улучшения)
4. **Эмодзи для визуализации**: Делают changelog более читаемым
5. **Ссылки на документацию**: Для сложных изменений

## 📋 Обязательная структура записи

```markdown
## 🔥 vX.Y.Z - Краткое описание релиза (YYYY-MM-DD)

### ✨ **Новые возможности:**
- **Название функции**
  - Подробное описание
  - Технические детали
  - Примеры использования

### 🐛 **Исправления:**
- **Проблема**: Описание бага
- **Решение**: Как исправлено
- **Влияние**: На что повлияло

### 🔧 **Улучшения:**
- **Что улучшено**: Конкретная область
- **Результат**: Какой эффект достигнут

### 🔄 **Изменения API/Breaking Changes:**
- **Что изменилось**: Конкретные изменения
- **Миграция**: Как обновиться
- **Совместимость**: Обратная совместимость

### 📁 **Новые/измененные файлы:**
```
├── path/to/new/file.ext        # Описание
├── path/to/changed/file.ext    # Что изменено
└── docs/NEW_FEATURE.md         # Документация
```

### 🚀 **Производительность:**
- Конкретные улучшения производительности
- Метрики до/после (если есть)

### 🔒 **Безопасность:**
- Исправления уязвимостей
- Улучшения безопасности

### 📱 **UX/UI:**
- Улучшения интерфейса
- Новые компоненты UI Kit
- Мобильная адаптация
```

## 🎨 Эмодзи для категорий

| Категория | Эмодзи | Использование |
|-----------|--------|---------------|
| Новые функции | ✨ | Новый функционал |
| Исправления | 🐛 | Баги и ошибки |
| Улучшения | 🔧 | Оптимизация существующего |
| Breaking Changes | 🔄 | Критические изменения |
| Безопасность | 🔒 | Вопросы безопасности |
| Производительность | 🚀 | Скорость и оптимизация |
| UI/UX | 📱 | Интерфейс и опыт |
| Документация | 📖 | Документация |
| Деплой | 🐳 | Docker, CI/CD |
| База данных | 🗄️ | Миграции, схема |

## 📝 Правила для AI

### При добавлении новой версии:

1. **Определить тип версии**:
   - PATCH (x.x.X): Исправления багов, мелкие улучшения
   - MINOR (x.X.x): Новые функции, обратно совместимые
   - MAJOR (X.x.x): Breaking changes, крупные изменения

2. **Обязательно указать**:
   - Дату релиза в формате (YYYY-MM-DD)
   - Краткое описание основной темы релиза
   - Все измененные файлы с описанием изменений
   - Ссылки на соответствующую документацию в /docs/

3. **Группировать изменения**:
   - Сначала новые функции (✨)
   - Затем исправления (🐛)
   - Потом улучшения (🔧)
   - В конце breaking changes (🔄)

4. **Для каждого изменения указать**:
   - **Что**: Конкретное изменение
   - **Зачем**: Причина изменения
   - **Как**: Техническая реализация (кратко)
   - **Где**: Затронутые файлы

5. **Обновить планы**:
   - Убрать выполненные пункты из "Планы на будущее"
   - Добавить новые планы если появились

## 🔗 Связь с документацией

Каждое значительное изменение должно иметь:
- Подробную документацию в `/docs/FEATURE_NAME.md`
- Ссылку на эту документацию в changelog
- Обновление основного README.md при критических изменениях

## 📊 Метрики для отслеживания

При возможности указывать:
- Время выполнения (до/после)
- Размер файлов (до/после)
- Количество строк кода
- Покрытие тестами
- Количество исправленных багов

## ✅ Чек-лист перед публикацией версии

- [ ] Все изменения задокументированы
- [ ] Указаны все измененные файлы
- [ ] Проверена обратная совместимость
- [ ] Обновлены планы на будущее
- [ ] Добавлены ссылки на документацию
- [ ] Проверена корректность семантической версии