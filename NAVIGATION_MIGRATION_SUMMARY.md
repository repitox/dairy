# 🚀 МИГРАЦИЯ НАВИГАЦИИ - КРАТКАЯ СВОДКА

## ✅ Готово к выполнению на продакшене

### 📊 Что будет сделано:
- Упрощение таблицы `navigation_items` с 21 поля до 7
- Четкое разделение dashboard/webapp через поле `platform`
- Сохранение всех активных данных
- Создание резервной копии

### 🎯 Результат:
```
Новая структура:
1. id - уникальный идентификатор
2. title - название пункта меню
3. url - ссылка
4. platform - 'dashboard' или 'webapp'
5. sort_order - порядок сортировки
6. parent_id - родитель (для иерархии)
7. is_active - активность
```

## 🚀 КОМАНДЫ ДЛЯ ВЫПОЛНЕНИЯ

### Вариант 1: Автоматический скрипт
```bash
python3 deploy_navigation_simplify.py
```

### Вариант 2: Ручное выполнение
```bash
# 1. Копируем файл
scp production_navigation_simplify.sql c107597@h60.netangels.ru:/tmp/

# 2. Выполняем миграцию
ssh c107597@h60.netangels.ru
export PGPASSWORD='ZoXboBiphobem19'
psql -h postgres.c107597.h2 -U c107597_dialist_ru -d c107597_dialist_ru -f /tmp/production_navigation_simplify.sql
```

## 🔄 ОТКАТ (если потребуется)
```bash
ssh c107597@h60.netangels.ru
export PGPASSWORD='ZoXboBiphobem19'
psql -h postgres.c107597.h2 -U c107597_dialist_ru -d c107597_dialist_ru -c "
DROP TABLE navigation_items;
ALTER TABLE navigation_items_backup_20250119 RENAME TO navigation_items;
"
```

## 📋 ПРОВЕРКА РЕЗУЛЬТАТА
```sql
SELECT 
    COUNT(*) as total,
    COUNT(CASE WHEN platform = 'dashboard' THEN 1 END) as dashboard,
    COUNT(CASE WHEN platform = 'webapp' THEN 1 END) as webapp
FROM navigation_items;
```

**Ожидаемый результат:** ~18 записей (8 dashboard + 10 webapp)

---
**Время выполнения:** ~30 секунд  
**Простой приложения:** НЕ требуется  
**Резервная копия:** navigation_items_backup_20250119