// WebApp Navigation Loader - адаптированная версия для Telegram WebApp
(function() {
    'use strict';
    
    // Конфигурация
    const CONFIG = {
        API_URL: '/api/navigation',
        CACHE_KEY: 'webapp_navigation_cache',
        CACHE_DURATION: 30 * 60 * 1000, // 30 минут
        FALLBACK_TIMEOUT: 3000, // 3 секунды на загрузку API
    };
    
    // Состояние загрузчика
    let isNavigationLoaded = false;
    let isLoading = false;
    let navigationCache = null;
    
    /**
     * Получение навигации из кеша
     */
    function getCachedNavigation() {
        try {
            const cached = localStorage.getItem(CONFIG.CACHE_KEY);
            if (!cached) return null;
            
            const data = JSON.parse(cached);
            const now = Date.now();
            
            // Проверяем срок годности кеша
            if (now - data.timestamp > CONFIG.CACHE_DURATION) {
                localStorage.removeItem(CONFIG.CACHE_KEY);
                return null;
            }
            
            console.log('📦 WebApp навигация загружена из кеша');
            return data.navigation;
            
        } catch (error) {
            console.warn('⚠️ Ошибка чтения кеша навигации:', error);
            localStorage.removeItem(CONFIG.CACHE_KEY);
            return null;
        }
    }
    
    /**
     * Сохранение навигации в кеш
     */
    function cacheNavigation(navigation) {
        try {
            const cacheData = {
                navigation: navigation,
                timestamp: Date.now(),
                version: '1.0'
            };
            
            localStorage.setItem(CONFIG.CACHE_KEY, JSON.stringify(cacheData));
            console.log('💾 WebApp навигация сохранена в кеш');
            
        } catch (error) {
            console.warn('⚠️ Ошибка сохранения кеша навигации:', error);
        }
    }
    
    /**
     * Загрузка навигации с API
     */
    async function fetchNavigationFromAPI() {
        try {
            // Получаем user_id для персонализации
            const userId = getUserId() || null;
            
            const params = new URLSearchParams();
            if (userId) params.append('user_id', userId);
            params.append('category', 'main'); // Используем категорию main для WebApp
            
            const response = await fetch(`${CONFIG.API_URL}?${params}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (!data.navigation || !Array.isArray(data.navigation)) {
                throw new Error('Invalid navigation data format');
            }
            
            // Фильтруем только WebApp пункты (без /dashboard/ в URL)
            const webappNavigation = data.navigation.filter(item => 
                !item.url.startsWith('/dashboard/') && 
                !item.url.includes('dashboard')
            );
            
            console.log('🌐 WebApp навигация загружена с API:', webappNavigation.length, 'пунктов');
            
            // Кешируем навигацию
            cacheNavigation(webappNavigation);
            
            return webappNavigation;
            
        } catch (error) {
            console.error('❌ Ошибка загрузки навигации с API:', error);
            throw error;
        }
    }
    
    /**
     * Получение fallback навигации
     */
    function getFallbackNavigation() {
        return [
            {
                id: 'home',
                title: 'Главная',
                url: 'index.html',
                icon: '🏠',
                category: 'main',
                sort_order: 1
            },
            {
                id: 'tasks',
                title: 'Задачи',
                url: 'tasks.html',
                icon: '📋',
                category: 'main',
                sort_order: 2
            },
            {
                id: 'events',
                title: 'События',
                url: 'events.html',
                icon: '📅',
                category: 'main',
                sort_order: 3
            },
            {
                id: 'shopping',
                title: 'Покупки',
                url: 'shopping.html',
                icon: '🛒',
                category: 'main',
                sort_order: 4
            },
            {
                id: 'projects',
                title: 'Все проекты',
                url: 'project_select.html',
                icon: '📁',
                category: 'projects',
                sort_order: 5
            },
            {
                id: 'project_create',
                title: 'Создать проект',
                url: 'project_create.html',
                icon: '➕',
                category: 'projects',
                sort_order: 6
            },
            {
                id: 'task_add',
                title: 'Новая задача',
                url: 'task_add.html',
                icon: '📝',
                category: 'create',
                sort_order: 7
            },
            {
                id: 'event_create',
                title: 'Новое событие',
                url: 'event_create.html',
                icon: '📅',
                category: 'create',
                sort_order: 8
            },
            {
                id: 'shopping_add',
                title: 'Добавить покупку',
                url: 'shopping.html',
                icon: '🛒',
                category: 'create',
                sort_order: 9
            },
            {
                id: 'settings',
                title: 'Настройки',
                url: 'settings.html',
                icon: '⚙️',
                category: 'settings',
                sort_order: 10
            },
            {
                id: 'timezone',
                title: 'Часовой пояс',
                url: 'timezone-settings.html',
                icon: '🌍',
                category: 'settings',
                sort_order: 11
            }
        ];
    }
    
    /**
     * Группировка навигации по категориям
     */
    function groupNavigationByCategory(navigationItems) {
        const groups = {
            main: { title: '📋 Основное', items: [] },
            projects: { title: '📁 Проекты', items: [] },
            create: { title: '➕ Создать', items: [] },
            settings: { title: '⚙️ Настройки', items: [] }
        };
        
        navigationItems.forEach(item => {
            const category = item.category || 'main';
            if (groups[category]) {
                groups[category].items.push(item);
            } else {
                groups.main.items.push(item);
            }
        });
        
        // Сортируем элементы в каждой группе
        Object.keys(groups).forEach(key => {
            groups[key].items.sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0));
        });
        
        return groups;
    }
    
    /**
     * Создание HTML для навигационного меню
     */
    function createNavigationMenuHTML(navigationItems) {
        const groups = groupNavigationByCategory(navigationItems);
        const currentPage = window.location.pathname.split('/').pop() || 'index.html';
        
        let sectionsHTML = '';
        
        Object.keys(groups).forEach(categoryKey => {
            const group = groups[categoryKey];
            if (group.items.length === 0) return;
            
            sectionsHTML += `
                <div class="nav-section">
                    <h4 class="nav-section-title">${group.title}</h4>
                    <div class="nav-links">
            `;
            
            group.items.forEach(item => {
                const isActive = currentPage === item.url.split('/').pop() ? 'active' : '';
                const badge = item.badge_text ? `<span class="nav-badge">${item.badge_text}</span>` : '';
                
                sectionsHTML += `
                    <a href="${item.url}" class="nav-item ${isActive}">
                        <span class="nav-item-icon">${item.icon}</span>
                        <span class="nav-item-text">${item.title}</span>
                        ${badge}
                    </a>
                `;
            });
            
            sectionsHTML += `
                    </div>
                </div>
            `;
        });
        
        return sectionsHTML;
    }
    
    /**
     * Обновление навигационного меню
     */
    function updateNavigationMenu(navigationItems) {
        const menuContainer = document.querySelector('.navigation-sections');
        if (!menuContainer) {
            console.warn('⚠️ Контейнер навигации не найден');
            return;
        }
        
        const navigationHTML = createNavigationMenuHTML(navigationItems);
        menuContainer.innerHTML = navigationHTML;
        
        console.log('✅ Навигационное меню обновлено из API');
    }
    
    /**
     * Добавление кнопки "Назад" для всех страниц кроме главной
     */
    function addBackButton() {
        const currentPage = window.location.pathname.split('/').pop() || 'index.html';
        
        // Не добавляем кнопку "Назад" на главной странице
        if (currentPage === 'index.html') {
            return;
        }
        
        const pageHeader = document.querySelector('.unified-page-header');
        if (!pageHeader) {
            console.warn('⚠️ Заголовок страницы не найден для добавления кнопки "Назад"');
            return;
        }
        
        // Проверяем, не добавлена ли уже кнопка
        if (pageHeader.querySelector('.back-button')) {
            return;
        }
        
        // Создаем кнопку "Назад"
        const backButton = document.createElement('button');
        backButton.className = 'back-button';
        backButton.onclick = () => {
            // Пытаемся вернуться назад в истории
            if (window.history.length > 1) {
                window.history.back();
            } else {
                // Если истории нет, переходим на главную
                window.location.href = 'index.html';
            }
        };
        backButton.innerHTML = `
            <span class="back-button-icon">←</span>
            <span class="back-button-text">Назад</span>
        `;
        
        // Вставляем кнопку в начало заголовка
        pageHeader.insertBefore(backButton, pageHeader.firstChild);
        
        console.log('✅ Кнопка "Назад" добавлена');
    }
    
    /**
     * Основная функция загрузки навигации
     */
    async function loadWebAppNavigation() {
        if (isNavigationLoaded || isLoading) {
            return;
        }
        
        isLoading = true;
        
        try {
            // Пытаемся загрузить из кеша
            let navigationItems = getCachedNavigation();
            
            if (!navigationItems) {
                // Загружаем с API
                try {
                    navigationItems = await Promise.race([
                        fetchNavigationFromAPI(),
                        new Promise((_, reject) => 
                            setTimeout(() => reject(new Error('Timeout')), CONFIG.FALLBACK_TIMEOUT)
                        )
                    ]);
                } catch (error) {
                    console.warn('⚠️ Используем fallback навигацию:', error.message);
                    navigationItems = getFallbackNavigation();
                }
            }
            
            // Обновляем навигационное меню
            updateNavigationMenu(navigationItems);
            
            // Добавляем кнопку "Назад"
            addBackButton();
            
            isNavigationLoaded = true;
            console.log('✅ WebApp навигация загружена успешно');
            
        } catch (error) {
            console.error('❌ Критическая ошибка загрузки навигации:', error);
            
            // В крайнем случае используем fallback
            const fallbackItems = getFallbackNavigation();
            updateNavigationMenu(fallbackItems);
            addBackButton();
            
        } finally {
            isLoading = false;
        }
    }
    
    /**
     * Функция для получения user_id (должна быть определена в других скриптах)
     */
    function getUserId() {
        // Пытаемся получить из Telegram WebApp
        if (window.Telegram?.WebApp?.initDataUnsafe?.user?.id) {
            return window.Telegram.WebApp.initDataUnsafe.user.id;
        }
        
        // Пытаемся получить из localStorage
        try {
            const userData = JSON.parse(localStorage.getItem('telegram_user') || '{}');
            return userData.id || null;
        } catch {
            return null;
        }
    }
    
    // Экспортируем функцию для использования в других скриптах
    window.loadWebAppNavigation = loadWebAppNavigation;
    
    // Автоматическая загрузка при готовности DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadWebAppNavigation);
    } else {
        loadWebAppNavigation();
    }
    
})();