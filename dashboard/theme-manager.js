/**
 * 🎨 Менеджер тем в стиле Telegram
 * Управляет переключением между светлой и темной темами
 */

class ThemeManager {
    constructor() {
        this.currentTheme = this.getStoredTheme() || this.getSystemTheme();
        this.init();
    }

    // Получить сохраненную тему из localStorage
    getStoredTheme() {
        return localStorage.getItem('theme');
    }

    // Получить системную тему
    getSystemTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }

    // Инициализация
    init() {
        this.applyTheme(this.currentTheme);
        this.setupSystemThemeListener();
        this.loadThemeFromDatabase();
        
        console.log(`🎨 Тема инициализирована: ${this.currentTheme}`);
    }

    // Загрузить тему из базы данных
    async loadThemeFromDatabase() {
        try {
            // Проверяем, есть ли Auth и пользователь
            if (typeof Auth !== 'undefined' && Auth.getCurrentUser) {
                const user = Auth.getCurrentUser();
                if (user && user.id) {
                    const response = await fetch(`/api/settings?user_id=${user.id}`);
                    if (response.ok) {
                        const settings = await response.json();
                        if (settings.theme && settings.theme !== this.currentTheme) {
                            this.setTheme(settings.theme);
                            console.log(`🎨 Тема загружена из БД: ${settings.theme}`);
                        }
                    }
                }
            }
        } catch (error) {
            console.log('🎨 Не удалось загрузить тему из БД, используем локальную:', error);
        }
    }

    // Применить тему
    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        this.currentTheme = theme;
        localStorage.setItem('theme', theme);
        
        // Обновляем кнопку переключения
        const toggle = document.querySelector('.theme-toggle');
        if (toggle) {
            toggle.setAttribute('data-theme', theme);
        }

        // Обновляем мета-тег для мобильных браузеров
        this.updateMetaThemeColor(theme);
        
        // Вызываем событие изменения темы
        this.dispatchThemeChangeEvent(theme);
    }

    // Переключить тему
    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
        
        console.log(`🎨 Тема изменена на: ${newTheme}`);
        
        // Анимация переключения
        this.animateThemeChange();
    }

    // Установить тему программно (для использования из настроек)
    setTheme(theme) {
        if (theme === 'auto') {
            // Для автоматической темы используем системную
            theme = this.getSystemTheme();
            localStorage.removeItem('theme-user-preference');
        } else {
            localStorage.setItem('theme-user-preference', 'true');
        }
        
        this.currentTheme = theme;
        this.applyTheme(theme);
        localStorage.setItem('theme', theme);
        console.log(`🎨 Тема установлена: ${theme}`);
    }



    // Обновить цвет мета-тега для мобильных браузеров
    updateMetaThemeColor(theme) {
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }

        const colors = {
            light: '#ffffff',
            dark: '#212121'
        };

        metaThemeColor.content = colors[theme];
    }

    // Слушатель изменения системной темы
    setupSystemThemeListener() {
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            
            mediaQuery.addEventListener('change', (e) => {
                // Применяем системную тему только если пользователь не выбрал тему вручную
                if (!localStorage.getItem('theme-user-preference')) {
                    const systemTheme = e.matches ? 'dark' : 'light';
                    this.applyTheme(systemTheme);
                    console.log(`🎨 Системная тема изменена на: ${systemTheme}`);
                }
            });
        }
    }

    // Анимация переключения темы
    animateThemeChange() {
        const toggle = document.querySelector('.theme-toggle');
        if (toggle) {
            toggle.style.transform = 'scale(0.9)';
            setTimeout(() => {
                toggle.style.transform = 'scale(1)';
            }, 150);
        }

        // Анимация всего документа
        document.body.style.transition = 'none';
        document.body.style.opacity = '0.95';
        
        setTimeout(() => {
            document.body.style.transition = '';
            document.body.style.opacity = '';
        }, 100);
    }

    // Отправить событие изменения темы
    dispatchThemeChangeEvent(theme) {
        const event = new CustomEvent('themechange', {
            detail: { theme }
        });
        document.dispatchEvent(event);
    }



    // Сбросить к системной теме
    resetToSystemTheme() {
        localStorage.removeItem('theme-user-preference');
        const systemTheme = this.getSystemTheme();
        this.applyTheme(systemTheme);
    }

    // Получить текущую тему
    getCurrentTheme() {
        return this.currentTheme;
    }

    // Проверить, темная ли тема
    isDarkTheme() {
        return this.currentTheme === 'dark';
    }

    // Получить CSS переменную текущей темы
    getCSSVariable(variable) {
        return getComputedStyle(document.documentElement).getPropertyValue(variable).trim();
    }
}

// Инициализация менеджера тем
let themeManager;

// Функция инициализации
function initThemeManager() {
    if (!themeManager) {
        themeManager = new ThemeManager();
        console.log('🎨 ThemeManager инициализирован');
    }
    return themeManager;
}

// Автоматическая инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    initThemeManager();
});

// Инициализация сразу, если DOM уже загружен
if (document.readyState === 'loading') {
    // DOM еще загружается, ждем события
} else {
    // DOM уже загружен
    initThemeManager();
}

// Экспорт для использования в других скриптах
window.ThemeManager = ThemeManager;
window.getThemeManager = () => themeManager;

// Утилиты для быстрого доступа
window.toggleTheme = () => {
    if (!themeManager) initThemeManager();
    return themeManager?.toggleTheme();
};
window.setTheme = (theme) => {
    if (!themeManager) initThemeManager();
    return themeManager?.setTheme(theme);
};
window.getCurrentTheme = () => {
    if (!themeManager) initThemeManager();
    return themeManager?.getCurrentTheme();
};
window.isDarkTheme = () => {
    if (!themeManager) initThemeManager();
    return themeManager?.isDarkTheme();
};

// Слушатель событий изменения темы для других скриптов
document.addEventListener('themechange', (e) => {
    console.log(`🎨 Событие изменения темы: ${e.detail.theme}`);
});

// Keyboard shortcut для переключения темы (Ctrl/Cmd + Shift + T)
document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {
        e.preventDefault();
        themeManager?.toggleTheme();
    }
});