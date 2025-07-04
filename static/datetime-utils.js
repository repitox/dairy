/**
 * Утилиты для работы с датами и временем в WebApp
 */

class WebAppDateTimeUtils {
    constructor(userId) {
        this.userId = userId;
        this.userTimezone = null;
        this.loadUserTimezone();
    }

    async loadUserTimezone() {
        try {
            if (this.userId) {
                const response = await fetch(`/api/user/timezone?user_id=${this.userId}`);
                if (response.ok) {
                    const data = await response.json();
                    this.userTimezone = parseInt(data.timezone) || 0;
                    console.log('🌍 Загружен часовой пояс пользователя:', this.userTimezone);
                }
            }
        } catch (error) {
            console.error('Ошибка загрузки часового пояса:', error);
            this.userTimezone = this.detectUserTimezone(); // Автоопределение
        }
    }

    async setUserTimezone(timezoneOffset) {
        try {
            if (!this.userId) return false;

            const response = await fetch('/api/user/timezone', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: this.userId,
                    timezone: timezoneOffset
                })
            });

            if (response.ok) {
                this.userTimezone = timezoneOffset;
                console.log('✅ Установлен часовой пояс:', timezoneOffset);
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
        const detectedOffset = Math.round(offset);
        console.log('🔍 Автоопределен часовой пояс:', detectedOffset);
        return detectedOffset;
    }

    /**
     * Группировать задачи по датам с учетом часового пояса
     */
    groupTasksByDate(tasks) {
        const now = new Date();
        const userOffset = this.getUserTimezone();
        
        // Создаем "сейчас" в часовом поясе пользователя
        const nowUser = new Date(now.getTime() + (userOffset * 60 * 60 * 1000));
        
        const grouped = {
            "Просроченные задачи": [],
            "Сегодня": [],
            "Завтра": [],
            "На неделе": [],
            "Позже": [],
            "Без срока": []
        };

        tasks.forEach(task => {
            if (task.completed) return;

            if (!task.due_date) {
                grouped["Без срока"].push(task);
                return;
            }

            // Парсим дату задачи
            const taskDate = this.parseTaskDate(task.due_date);
            if (!taskDate) {
                grouped["Без срока"].push(task);
                return;
            }

            // Конвертируем в часовой пояс пользователя
            const taskDateUser = new Date(taskDate.getTime() + (userOffset * 60 * 60 * 1000));
            
            console.log(`📅 Задача "${task.title}":`, {
                due_date: task.due_date,
                taskDate: taskDate.toISOString(),
                taskDateUser: taskDateUser.toISOString(),
                nowUser: nowUser.toISOString(),
                isToday: this.isSameDay(taskDateUser, nowUser),
                isTomorrow: this.isSameDay(taskDateUser, new Date(nowUser.getTime() + 24*60*60*1000)),
                isPast: taskDateUser < nowUser
            });

            if (taskDateUser < nowUser) {
                grouped["Просроченные задачи"].push(task);
            } else if (this.isSameDay(taskDateUser, nowUser)) {
                grouped["Сегодня"].push(task);
            } else if (this.isSameDay(taskDateUser, new Date(nowUser.getTime() + 24*60*60*1000))) {
                grouped["Завтра"].push(task);
            } else if (this.isSameWeek(taskDateUser, nowUser)) {
                grouped["На неделе"].push(task);
            } else {
                grouped["Позже"].push(task);
            }
        });

        return grouped;
    }

    /**
     * Парсить дату задачи
     */
    parseTaskDate(dateString) {
        if (!dateString) return null;

        try {
            // Пробуем разные форматы
            const formats = [
                /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/, // 2025-07-02T19:00:00
                /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/,       // 2025-07-02T19:00
                /^\d{4}-\d{2}-\d{2}$/                    // 2025-07-02
            ];

            let parsedDate;
            
            if (formats[0].test(dateString) || formats[1].test(dateString)) {
                // Дата с временем - считаем UTC
                parsedDate = new Date(dateString + (dateString.includes('Z') ? '' : 'Z'));
            } else if (formats[2].test(dateString)) {
                // Только дата - добавляем время 00:00 в часовом поясе пользователя
                const userOffset = this.getUserTimezone();
                parsedDate = new Date(dateString + 'T00:00:00Z');
                // Корректируем на часовой пояс пользователя
                parsedDate = new Date(parsedDate.getTime() - (userOffset * 60 * 60 * 1000));
            } else {
                parsedDate = new Date(dateString);
            }

            return isNaN(parsedDate.getTime()) ? null : parsedDate;
        } catch (error) {
            console.error('Ошибка парсинга даты:', dateString, error);
            return null;
        }
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
     * Проверить, что две даты в одной неделе
     */
    isSameWeek(date1, date2) {
        const startOfWeek1 = new Date(date1);
        startOfWeek1.setDate(date1.getDate() - date1.getDay() + 1); // Понедельник
        startOfWeek1.setHours(0, 0, 0, 0);

        const startOfWeek2 = new Date(date2);
        startOfWeek2.setDate(date2.getDate() - date2.getDay() + 1); // Понедельник
        startOfWeek2.setHours(0, 0, 0, 0);

        return startOfWeek1.getTime() === startOfWeek2.getTime();
    }

    /**
     * Форматировать дату для отображения
     */
    formatDate(dateString, format = 'relative') {
        if (!dateString) return '';
        
        const date = this.parseTaskDate(dateString);
        if (!date) return '';
        
        const userOffset = this.getUserTimezone();
        const userDate = new Date(date.getTime() + (userOffset * 60 * 60 * 1000));
        
        if (format === 'relative') {
            return this.getRelativeDateText(userDate);
        } else if (format === 'full') {
            return userDate.toLocaleString('ru-RU', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } else if (format === 'date') {
            return userDate.toLocaleDateString('ru-RU');
        } else if (format === 'time') {
            return userDate.toLocaleTimeString('ru-RU', {
                hour: '2-digit',
                minute: '2-digit'
            });
        }
        
        return userDate.toLocaleString('ru-RU');
    }

    /**
     * Получить относительный текст даты
     */
    getRelativeDateText(userDate) {
        const now = new Date();
        const userOffset = this.getUserTimezone();
        const nowUser = new Date(now.getTime() + (userOffset * 60 * 60 * 1000));
        
        // Сравниваем только даты
        const dateOnly = new Date(userDate.getFullYear(), userDate.getMonth(), userDate.getDate());
        const nowOnly = new Date(nowUser.getFullYear(), nowUser.getMonth(), nowUser.getDate());
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
            return userDate.toLocaleDateString('ru-RU', { 
                day: 'numeric', 
                month: 'short' 
            });
        }
    }

    /**
     * Автоматически установить часовой пояс при первом запуске
     */
    async autoSetTimezoneIfNeeded() {
        if (this.userTimezone === null || this.userTimezone === 0) {
            const detectedTz = this.detectUserTimezone();
            if (detectedTz !== 0) {
                await this.setUserTimezone(detectedTz);
            }
        }
    }
}

// Экспортируем класс для использования
window.WebAppDateTimeUtils = WebAppDateTimeUtils;