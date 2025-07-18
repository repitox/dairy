# Исправление отображения времени встреч

## Проблема

На странице `/dashboard/meetings.html` встречи без времени окончания отображались с "фиктивным" временем окончания (например, "19.07.2025, 14:00 - 03:00" вместо "19.07.2025, 14:00").

## Причина

В коде JavaScript создавался объект `Date` из значения `null` для времени окончания:

```javascript
// Проблемный код
const endDate = new Date(meeting.end_at); // meeting.end_at может быть null
// ...
${formatDateTime(startDate)} - ${formatTime(endDate)} // endDate = Invalid Date
```

Когда `meeting.end_at` равно `null`, `new Date(null)` создает дату "1970-01-01T00:00:00.000Z", которая при форматировании в московском часовом поясе отображается как "03:00".

## Решение

Обновлен код для корректной обработки отсутствующих значений времени:

### До исправления:
```javascript
const startDate = new Date(meeting.start_at);
const endDate = new Date(meeting.end_at);
// ...
${formatDateTime(startDate)} - ${formatTime(endDate)}
```

### После исправления:
```javascript
const startDate = meeting.start_at ? new Date(meeting.start_at) : null;
const endDate = meeting.end_at ? new Date(meeting.end_at) : null;
// ...
${startDate || endDate ? `
    <div class="meeting-time">
        <span>🕐</span>
        ${startDate ? formatDateTime(startDate) : 'Время не указано'}${endDate ? ` - ${formatTime(endDate)}` : ''}
    </div>
` : ''}
```

## Логика отображения времени

### Различные сценарии:

1. **Полная встреча** (`start_at` и `end_at` заданы):
   - Отображение: `"19.07.2025, 14:00 - 17:00"`

2. **Встреча только с началом** (`start_at` задан, `end_at` = null):
   - Отображение: `"19.07.2025, 14:00"`

3. **Встреча без времени** (`start_at` и `end_at` = null):
   - Время не отображается вообще

4. **Встреча только с окончанием** (`start_at` = null, `end_at` задан):
   - Отображение: `"Время не указано - 17:00"`

## Обновленные функции

### Проверка статуса встречи
```javascript
const isToday = startDate ? isDateToday(startDate) : false;
const isPast = startDate ? startDate < new Date() : false;
```

Теперь статус встречи определяется только при наличии времени начала.

### Условное отображение
```javascript
${startDate || endDate ? `
    <div class="meeting-time">
        <span>🕐</span>
        ${startDate ? formatDateTime(startDate) : 'Время не указано'}${endDate ? ` - ${formatTime(endDate)}` : ''}
    </div>
` : ''}
```

Блок времени отображается только если есть хотя бы одно из времен.

## Совместимость

### Поддерживаемые форматы данных:
- ✅ `start_at: "2025-07-19T14:00:00"`, `end_at: "2025-07-19T17:00:00"`
- ✅ `start_at: "2025-07-19T14:00:00"`, `end_at: null`
- ✅ `start_at: null`, `end_at: "2025-07-19T17:00:00"`
- ✅ `start_at: null`, `end_at: null`

### Страницы:
- ✅ `/dashboard/meetings.html` - исправлено
- ✅ `/dashboard/view-meeting.html` - уже работало корректно

## Тестирование

### Тестовые встречи:
- **ID 17**: `start_at: "2025-07-19T14:00:00"`, `end_at: null`
  - Было: "19.07.2025, 14:00 - 03:00"
  - Стало: "19.07.2025, 14:00"

- **ID 16**: `start_at: null`, `end_at: null`
  - Было: "Invalid Date - 03:00"
  - Стало: время не отображается

## Дополнительные исправления

### Проблема с фильтрацией встреч
Обнаружена вторая проблема: функция `filterMeetings` не учитывала возможность `null` значений для `start_at`, что приводило к ошибкам при фильтрации.

### Исправление фильтрации
```javascript
// Было
filteredMeetings = filteredMeetings.filter(meeting => 
    new Date(meeting.start_at) > now
);

// Стало
filteredMeetings = filteredMeetings.filter(meeting => 
    meeting.start_at && new Date(meeting.start_at) > now
);
```

## Файлы изменены

- `/dashboard/meetings.html` - исправлена логика отображения времени и фильтрации
- `/docs/MEETING_TIME_DISPLAY_FIX.md` - документация исправления

## Результат

Теперь встречи корректно отображают время в зависимости от наличия данных:
- 🕐 Полное время для встреч с началом и окончанием
- 🕐 Только время начала для встреч без окончания
- ⏰ Отсутствие времени для встреч без временных данных
- 🚫 Никаких "фиктивных" времен типа "03:00"

Исправление обеспечивает корректное отображение всех типов встреч, включая новую функциональность создания встреч без обязательного времени.