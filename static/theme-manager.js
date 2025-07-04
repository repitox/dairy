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
        this.createToggleButton();
        this.setupSystemThemeListener();
        
        console.log(`🎨 Тема инициализирована: ${this.currentTheme}`);
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

    // Создать кнопку переключения темы
    createToggleButton() {
        // Проверяем, есть ли уже кнопка
        if (document.querySelector('.theme-toggle')) {
            return;
        }

        const toggle = document.createElement('button');
        toggle.className = 'theme-toggle';
        toggle.setAttribute('data-theme', this.currentTheme);
        toggle.setAttribute('title', 'Переключить тему');
        toggle.setAttribute('aria-label', 'Переключить тему');
        
        const icon = document.createElement('span');
        icon.className = 'theme-icon';
        toggle.appendChild(icon);

        toggle.addEventListener('click', () => this.toggleTheme());
        
        document.body.appendChild(toggle);
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

    // Установить тему программно
    setTheme(theme) {
        if (['light', 'dark'].includes(theme)) {
            localStorage.setItem('theme-user-preference', 'true');
            this.applyTheme(theme);
        }
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

// Автоматическая инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    themeManager = new ThemeManager();
});

// Экспорт для использования в других скриптах
window.ThemeManager = ThemeManager;
window.getThemeManager = () => themeManager;

// Утилиты для быстрого доступа
window.toggleTheme = () => themeManager?.toggleTheme();
window.setTheme = (theme) => themeManager?.setTheme(theme);
window.getCurrentTheme = () => themeManager?.getCurrentTheme();
window.isDarkTheme = () => themeManager?.isDarkTheme();

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