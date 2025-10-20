/**
 * Утилиты для работы с датами и временем в Dashboard
 */

class DateTimeUtils {
    constructor() {
        this.userTimezone = null;
        // Не загружаем автоматически в конструкторе
    }

    async loadUserTimezone() {
        try {
            const user = Auth.getCurrentUser();
            if (user) {
                const response = await fetch(`/api/user/timezone?user_id=${user.id}`);
                if (response.ok) {
                    const data = await response.json();
                    this.userTimezone = parseInt(data.timezone) || 0;
                }
            }
        } catch (error) {
            console.error('Ошибка загрузки часового пояса:', error);
            this.userTimezone = 0; // UTC по умолчанию
        }
    }

    async setUserTimezone(timezoneOffset) {
        try {
            const user = Auth.getCurrentUser();
            if (!user) return false;

            const response = await fetch('/api/user/timezone', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: user.id,
                    timezone: timezoneOffset
                })
            });

            if (response.ok) {
                this.userTimezone = timezoneOffset;
                return true;
            }
        } catch (error) {
            console.error('Ошибка установки часового пояса:', error);
        }
        return false;
    }

    getUserTimezone() {
        return this.userTimezone !== null ? this.userTimezone : 0;
    }

    /**
     * Автоматически определить часовой пояс пользователя
     */
    detectUserTimezone() {
        const offset = -new Date().getTimezoneOffset() / 60;
        return Math.round(offset);
    }

    /**
     * Конвертировать UTC время в локальное время пользователя
     */
    utcToUserTime(utcDateString) {
        if (!utcDateString) return null;
        
        // Убираем 'Z' если есть и парсим как UTC
        const cleanDateString = utcDateString.replace('Z', '');
        const utcDate = new Date(cleanDateString + 'Z'); // Принудительно указываем UTC
        
        const userOffset = this.getUserTimezone();
        const userDate = new Date(utcDate.getTime() + (userOffset * 60 * 60 * 1000));
        
        return userDate;
    }

    /**
     * Конвертировать локальное время пользователя в UTC
     */
    userTimeToUtc(userDateString) {
        if (!userDateString) return null;
        
        // Парсим как локальное время (без указания часового пояса)
        const userDate = new Date(userDateString);
        const userOffset = this.getUserTimezone();
        const utcDate = new Date(userDate.getTime() - (userOffset * 60 * 60 * 1000));
        
        return utcDate;
    }

    /**
     * Форматировать дату для отображения
     */
    formatDate(dateString, format = 'relative') {
        if (!dateString) return '';
        
        const date = this.utcToUserTime(dateString);
        if (!date) return '';
        
        const now = new Date();
        
        if (format === 'relative') {
            return this.getRelativeDateText(date, now);
        } else if (format === 'full') {
            return date.toLocaleString('ru-RU', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } else if (format === 'date') {
            return date.toLocaleDateString('ru-RU');
        } else if (format === 'time') {
            return date.toLocaleTimeString('ru-RU', {
                hour: '2-digit',
                minute: '2-digit'
            });
        }
        
        return date.toLocaleString('ru-RU');
    }

    /**
     * Получить относительный текст даты
     */
    getRelativeDateText(date, now = new Date()) {
        // Сравниваем только даты, игнорируя время
        const dateOnly = new Date(date.getFullYear(), date.getMonth(), date.getDate());
        const nowOnly = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const diffTime = dateOnly - nowOnly;
        const diffDays = diffTime / (1000 * 60 * 60 * 24);

        if (diffDays < 0) {
            return `${Math.abs(diffDays)}д назад`;
        } else if (diffDays === 0) {
            return 'Сегодня';
        } else if (diffDays === 1) {
            return 'Завтра';
        } else if (diffDays <= 7) {
            return `${diffDays}д`;
        } else {
            return date.toLocaleDateString('ru-RU', { 
                day: 'numeric', 
                month: 'short' 
            });
        }
    }

    /**
     * Проверить, что дата сегодня
     */
    isToday(dateString) {
        if (!dateString) return false;
        
        const date = this.utcToUserTime(dateString);
        const now = new Date();
        
        return this.isSameDay(date, now);
    }

    /**
     * Проверить, что дата завтра
     */
    isTomorrow(dateString) {
        if (!dateString) return false;
        
        const date = this.utcToUserTime(dateString);
        const now = new Date();
        const tomorrow = new Date(now);
        tomorrow.setDate(tomorrow.getDate() + 1);
        
        return this.isSameDay(date, tomorrow);
    }

    /**
     * Проверить, что дата просрочена
     */
    isOverdue(dateString) {
        if (!dateString) return false;
        
        const date = this.utcToUserTime(dateString);
        const now = new Date();
        
        return date < now;
    }

    /**
     * Проверить, что две даты в один день
     */
    isSameDay(date1, date2) {
        return date1.getFullYear() === date2.getFullYear() &&
               date1.getMonth() === date2.getMonth() &&
               date1.getDate() === date2.getDate();
    }

    /**
     * Получить CSS класс для даты
     */
    getDateClass(dateString) {
        if (!dateString) return '';
        
        if (this.isOverdue(dateString)) {
            return 'overdue';
        } else if (this.isToday(dateString)) {
            return 'today';
        }
        
        return '';
    }

    /**
     * Создать input datetime-local с учетом часового пояса
     */
    createDateTimeInput(value = null) {
        const input = document.createElement('input');
        input.type = 'datetime-local';
        
        if (value) {
            const userDate = this.utcToUserTime(value);
            if (userDate) {
                // Форматируем для datetime-local
                const year = userDate.getFullYear();
                const month = String(userDate.getMonth() + 1).padStart(2, '0');
                const day = String(userDate.getDate()).padStart(2, '0');
                const hours = String(userDate.getHours()).padStart(2, '0');
                const minutes = String(userDate.getMinutes()).padStart(2, '0');
                
                input.value = `${year}-${month}-${day}T${hours}:${minutes}`;
            }
        }
        
        return input;
    }

    /**
     * Получить UTC дату из datetime-local input
     */
    getUtcFromDateTimeInput(input) {
        if (!input.value) return null;
        
        // datetime-local возвращает локальное время пользователя
        const userDate = new Date(input.value);
        return this.userTimeToUtc(userDate.toISOString());
    }

    /**
     * Инициализация утилит
     */
    async init() {
        await this.loadUserTimezone();
    }
}

// Создаем глобальный экземпляр
window.DateTimeUtils = new DateTimeUtils();

// Добавляем init как функцию к экземпляру (на случай проблем с методами класса)
window.DateTimeUtils.init = async function() {
    await this.loadUserTimezone();
};

// Добавляем все методы к экземпляру для обеспечения доступности
const instance = window.DateTimeUtils;
const prototype = Object.getPrototypeOf(instance);
const methodNames = Object.getOwnPropertyNames(prototype);

methodNames.forEach(methodName => {
    if (methodName !== 'constructor' && typeof prototype[methodName] === 'function') {
        // Принудительно добавляем метод к экземпляру
        instance[methodName] = prototype[methodName].bind(instance);
    }
});

// Дополнительно добавляем ключевые методы явно
instance.getUserTimezone = function() {
    return this.userTimezone !== null ? this.userTimezone : 0;
};

instance.loadUserTimezone = async function() {
    try {
        const user = Auth.getCurrentUser();
        if (user) {
            const response = await fetch(`/api/user/timezone?user_id=${user.id}`);
            if (response.ok) {
                const data = await response.json();
                this.userTimezone = parseInt(data.timezone) || 0;
            }
        }
    } catch (error) {
        console.error('Ошибка загрузки часового пояса:', error);
        this.userTimezone = 0; // UTC по умолчанию
    }
};

instance.setUserTimezone = async function(timezoneOffset) {
    try {
        const user = Auth.getCurrentUser();
        if (!user) return false;

        const response = await fetch('/api/user/timezone', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: user.id,
                timezone: timezoneOffset
            })
        });

        if (response.ok) {
            this.userTimezone = timezoneOffset;
            return true;
        }
    } catch (error) {
        console.error('Ошибка установки часового пояса:', error);
    }
    return false;
};

instance.detectUserTimezone = function() {
    const offset = -new Date().getTimezoneOffset() / 60;
    return Math.round(offset);
};

// Отладочная информация
console.log('🔧 DateTimeUtils создан v5, методы прототипа:', Object.getOwnPropertyNames(Object.getPrototypeOf(window.DateTimeUtils)));
console.log('🔧 DateTimeUtils методы экземпляра:', Object.getOwnPropertyNames(window.DateTimeUtils));
console.log('🔧 DateTimeUtils.init доступен:', typeof window.DateTimeUtils.init);
console.log('🔧 DateTimeUtils.getUserTimezone доступен:', typeof window.DateTimeUtils.getUserTimezone);
console.log('🔧 DateTimeUtils.loadUserTimezone доступен:', typeof window.DateTimeUtils.loadUserTimezone);
console.log('🔧 DateTimeUtils.setUserTimezone доступен:', typeof window.DateTimeUtils.setUserTimezone);
console.log('🔧 DateTimeUtils.detectUserTimezone доступен:', typeof window.DateTimeUtils.detectUserTimezone);
