/**
 * 🎨 Менеджер тем для Telegram WebApp
 * Интегрируется с настройками Telegram и использует единую систему тем
 */

class WebAppThemeManager {
    constructor() {
        this.tg = window.Telegram?.WebApp;
        this.currentTheme = this.getInitialTheme();
        this.init();
    }

    // Получить начальную тему
    getInitialTheme() {
        // 1. Проверяем сохраненную пользователем тему
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme && ['light', 'dark'].includes(savedTheme)) {
            return savedTheme;
        }

        // 2. Используем тему Telegram если доступна
        if (this.tg && this.tg.colorScheme) {
            return this.tg.colorScheme === 'dark' ? 'dark' : 'light';
        }

        // 3. Используем системную тему
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }

        // 4. По умолчанию светлая тема
        return 'light';
    }

    // Инициализация
    init() {
        this.applyTheme(this.currentTheme);
        this.setupTelegramThemeListener();
        this.setupSystemThemeListener();
        this.createToggleButton();
        
        console.log(`🎨 WebApp тема инициализирована: ${this.currentTheme}`);
        
        // Синхронизируем с Telegram WebApp
        this.syncWithTelegramWebApp();
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
        
        // Синхронизируем с Telegram WebApp
        this.syncWithTelegramWebApp();
        
        // Вызываем событие изменения темы
        this.dispatchThemeChangeEvent(theme);
    }

    // Переключить тему
    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
        
        console.log(`🎨 WebApp тема изменена на: ${newTheme}`);
        
        // Анимация переключения
        this.animateThemeChange();
        
        // Отправляем haptic feedback если доступен
        if (this.tg && this.tg.HapticFeedback) {
            this.tg.HapticFeedback.impactOccurred('light');
        }
    }

    // Создать кнопку переключения темы
    createToggleButton() {
        // Проверяем, есть ли уже кнопка
        if (document.querySelector('.theme-toggle')) {
            return;
        }

        const toggle = document.createElement('button');
        toggle.className = 'theme-toggle webapp-theme-toggle';
        toggle.setAttribute('data-theme', this.currentTheme);
        toggle.setAttribute('title', 'Переключить тему');
        toggle.setAttribute('aria-label', 'Переключить тему');
        
        const icon = document.createElement('span');
        icon.className = 'theme-icon';
        toggle.appendChild(icon);

        // Специальные стили для WebApp
        toggle.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 1000;
            background-color: var(--bg-card);
            border: 1px solid var(--border-medium);
            border-radius: 50px;
            padding: 8px;
            cursor: pointer;
            box-shadow: 0 2px 8px var(--shadow-medium);
            transition: all var(--transition-fast);
            display: flex;
            align-items: center;
            gap: 8px;
            min-width: 40px;
            height: 40px;
            justify-content: center;
        `;

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

    // Слушатель изменения темы Telegram
    setupTelegramThemeListener() {
        if (this.tg && this.tg.onEvent) {
            this.tg.onEvent('themeChanged', () => {
                // Применяем тему Telegram только если пользователь не выбрал тему вручную
                if (!localStorage.getItem('theme-user-preference')) {
                    const telegramTheme = this.tg.colorScheme === 'dark' ? 'dark' : 'light';
                    this.applyTheme(telegramTheme);
                    console.log(`🎨 Тема изменена по Telegram: ${telegramTheme}`);
                }
            });
        }
    }

    // Слушатель изменения системной темы
    setupSystemThemeListener() {
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            
            mediaQuery.addEventListener('change', (e) => {
                // Применяем системную тему только если пользователь не выбрал тему вручную
                if (!localStorage.getItem('theme-user-preference') && (!this.tg || !this.tg.colorScheme)) {
                    const systemTheme = e.matches ? 'dark' : 'light';
                    this.applyTheme(systemTheme);
                    console.log(`🎨 Системная тема изменена на: ${systemTheme}`);
                }
            });
        }
    }

    // Синхронизация с Telegram WebApp
    syncWithTelegramWebApp() {
        if (!this.tg) return;

        try {
            // Устанавливаем цвет заголовка
            const headerColor = this.currentTheme === 'dark' ? '#212121' : '#ffffff';
            if (this.tg.setHeaderColor) {
                this.tg.setHeaderColor(headerColor);
            }

            // Устанавливаем цвет фона
            const bgColor = this.currentTheme === 'dark' ? '#212121' : '#ffffff';
            if (this.tg.setBackgroundColor) {
                this.tg.setBackgroundColor(bgColor);
            }

            // Обновляем главную кнопку если есть
            if (this.tg.MainButton && this.tg.MainButton.isVisible) {
                const buttonColor = this.currentTheme === 'dark' ? '#54a9eb' : '#0088cc';
                this.tg.MainButton.color = buttonColor;
            }

        } catch (error) {
            console.warn('⚠️ Ошибка синхронизации с Telegram WebApp:', error);
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
            detail: { theme, source: 'webapp' }
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

    // Сбросить к автоматической теме
    resetToAutoTheme() {
        localStorage.removeItem('theme-user-preference');
        const autoTheme = this.getInitialTheme();
        this.applyTheme(autoTheme);
    }

    // Получить текущую тему
    getCurrentTheme() {
        return this.currentTheme;
    }

    // Проверить, темная ли тема
    isDarkTheme() {
        return this.currentTheme === 'dark';
    }

    // Получить информацию о Telegram WebApp
    getTelegramInfo() {
        if (!this.tg) return null;
        
        return {
            colorScheme: this.tg.colorScheme,
            themeParams: this.tg.themeParams,
            platform: this.tg.platform,
            version: this.tg.version
        };
    }
}

// Инициализация менеджера тем для WebApp
let webAppThemeManager;

// Автоматическая инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    webAppThemeManager = new WebAppThemeManager();
});

// Экспорт для использования в других скриптах
window.WebAppThemeManager = WebAppThemeManager;
window.getWebAppThemeManager = () => webAppThemeManager;

// Утилиты для быстрого доступа
window.toggleTheme = () => webAppThemeManager?.toggleTheme();
window.setTheme = (theme) => webAppThemeManager?.setTheme(theme);
window.getCurrentTheme = () => webAppThemeManager?.getCurrentTheme();
window.isDarkTheme = () => webAppThemeManager?.isDarkTheme();

// Слушатель событий изменения темы для других скриптов
document.addEventListener('themechange', (e) => {
    console.log(`🎨 WebApp событие изменения темы: ${e.detail.theme}`);
});

// Keyboard shortcut для переключения темы (Ctrl/Cmd + Shift + T)
document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {
        e.preventDefault();
        webAppThemeManager?.toggleTheme();
    }
});

// Интеграция с настройками Telegram WebApp
if (window.Telegram?.WebApp) {
    const tg = window.Telegram.WebApp;
    
    // Расширяем WebApp при инициализации
    tg.ready(() => {
        tg.expand();
        console.log('🚀 Telegram WebApp готов, тема:', tg.colorScheme);
    });
}