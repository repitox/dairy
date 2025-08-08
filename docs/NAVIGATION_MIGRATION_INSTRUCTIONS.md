# 🚀 Инструкция по миграции навигации на продакшен

## 📋 Обзор

Миграция упрощает структуру таблицы `navigation_items` с 21 поля до 7 основных полей и добавляет четкое разделение между dashboard и webapp.

## 🎯 Цель миграции

- ✅ Упростить структуру БД
- ✅ Четко разделить dashboard и webapp навигацию
- ✅ Подготовить основу для иерархической навигации
- ✅ Убрать избыточные поля

## 🔧 Способы выполнения

### Способ 1: Автоматический скрипт (рекомендуется)

```bash
cd /Users/d.dubenetskiy/Documents/tg_project
python3 deploy_navigation_simplify.py
```

### Способ 2: Ручное выполнение

1. **Копируем SQL файл на сервер:**
```bash
scp production_navigation_simplify.sql c107597@h60.netangels.ru:/tmp/
```

2. **Подключаемся к серверу:**
```bash
ssh c107597@h60.netangels.ru
```

3. **Выполняем миграцию:**
```bash
export PGPASSWORD='ZoXboBiphobem19'
psql -h postgres.c107597.h2 -U c107597_dialist_ru -d c107597_dialist_ru -f /tmp/production_navigation_simplify.sql
```

### Способ 3: Через SSH одной командой

```bash
ssh c107597@h60.netangels.ru "export PGPASSWORD='ZoXboBiphobem19' && psql -h postgres.c107597.h2 -U c107597_dialist_ru -d c107597_dialist_ru" < production_navigation_simplify.sql
```

## 📊 Ожидаемый результат

После выполнения миграции:

- **Новая структура:** 7 полей вместо 21
- **Платформы:** четкое разделение dashboard/webapp
- **Резервная копия:** `navigation_items_backup_20250119`
- **Данные:** все активные элементы сохранены

### Новые поля:
1. `id` - уникальный идентификатор
2. `title` - название пункта меню
3. `url` - ссылка на страницу
4. `platform` - 'dashboard' или 'webapp'
5. `sort_order` - порядок сортировки
6. `parent_id` - родительский элемент
7. `is_active` - активность элемента

## 🔍 Проверка результата

После миграции проверьте:

```sql
-- Общая статистика
SELECT 
    COUNT(*) as total,
    COUNT(CASE WHEN platform = 'dashboard' THEN 1 END) as dashboard,
    COUNT(CASE WHEN platform = 'webapp' THEN 1 END) as webapp
FROM navigation_items;

-- Структура таблицы
\d navigation_items

-- Примеры данных
SELECT id, title, url, platform, sort_order 
FROM navigation_items 
ORDER BY platform, sort_order 
LIMIT 10;
```

## 🔄 Откат миграции

Если что-то пошло не так, можно откатить миграцию:

```bash
ssh c107597@h60.netangels.ru
export PGPASSWORD='ZoXboBiphobem19'
psql -h postgres.c107597.h2 -U c107597_dialist_ru -d c107597_dialist_ru -c "
DROP TABLE navigation_items;
ALTER TABLE navigation_items_backup_20250119 RENAME TO navigation_items;
"
```

## ⚠️ Важные моменты

1. **Резервная копия:** Старая таблица сохраняется как `navigation_items_backup_20250119`
2. **Время выполнения:** ~30 секунд
3. **Простой приложения:** Не требуется
4. **Совместимость:** Код приложения должен быть обновлен для работы с новой структурой

## 📝 Логи

Миграция выводит подробные логи:
- 🔍 Текущая структура и данные
- 📝 Процесс создания новой таблицы
- 📦 Перенос данных
- 📊 Статистика результата
- ✅ Подтверждение успешного завершения

## 🆘 Поддержка

Если возникли проблемы:

1. Проверьте логи миграции
2. Убедитесь в доступности БД
3. Проверьте права доступа
4. При необходимости выполните откат

## 📅 Дата выполнения

- **Разработано:** 2025-01-19
- **Тестировано локально:** ✅
- **Готово к продакшену:** ✅