// Умный загрузчик навигации на основе API с предотвращением прыжков
(function() {
    'use strict';
    
    // Конфигурация
    const CONFIG = {
        API_URL: '/api/navigation',
        CACHE_KEY: 'navigation_cache',
        CACHE_DURATION: 30 * 60 * 1000, // 30 минут
        FALLBACK_TIMEOUT: 3000, // 3 секунды на загрузку API
        SKELETON_DURATION: 150, // Время показа skeleton после загрузки
    };
    
    // Состояние загрузчика
    let isNavigationLoaded = false;
    let isLoading = false;
    let navigationCache = null;
    
    /**
     * Создание skeleton навигации для предотвращения прыжков
     */
    function createNavigationSkeleton() {
        // Проверяем, не создан ли уже skeleton
        if (document.querySelector('.api-navigation-skeleton')) {
            return;
        }
        
        // Создаем navbar skeleton
        const navbarSkeleton = document.createElement('nav');
        navbarSkeleton.className = 'api-navigation-skeleton api-navbar-skeleton';
        navbarSkeleton.innerHTML = `
            <div class="api-navbar-brand-skeleton"></div>
            <div class="api-navbar-actions-skeleton">
                <div class="api-navbar-user-skeleton"></div>
            </div>
        `;
        
        // Создаем sidebar skeleton
        const sidebarSkeleton = document.createElement('div');
        sidebarSkeleton.className = 'api-navigation-skeleton api-sidebar-skeleton';
        
        // Добавляем skeleton элементы меню
        const menuSkeleton = document.createElement('div');
        menuSkeleton.className = 'api-menu-skeleton';
        
        for (let i = 0; i < 8; i++) {
            const itemSkeleton = document.createElement('div');
            itemSkeleton.className = 'api-menu-item-skeleton';
            itemSkeleton.style.animationDelay = `${i * 0.1}s`;
            menuSkeleton.appendChild(itemSkeleton);
        }
        
        sidebarSkeleton.appendChild(menuSkeleton);
        
        // Вставляем skeleton в DOM
        document.body.insertAdjacentElement('afterbegin', navbarSkeleton);
        document.body.insertAdjacentElement('afterbegin', sidebarSkeleton);
        
        // Резервируем место для контента
        document.body.classList.add('api-navigation-loading');
        
        console.log('🔮 API Navigation skeleton создан');
    }
    
    /**
     * Удаление skeleton навигации
     */
    function removeNavigationSkeleton() {
        const skeletons = document.querySelectorAll('.api-navigation-skeleton');
        
        skeletons.forEach(skeleton => {
            skeleton.style.opacity = '0';
            skeleton.style.transform = 'translateY(-10px)';
            
            setTimeout(() => {
                if (skeleton.parentNode) {
                    skeleton.parentNode.removeChild(skeleton);
                }
            }, 300);
        });
        
        document.body.classList.remove('api-navigation-loading');
        document.body.classList.add('api-navigation-loaded');
        
        console.log('✅ API Navigation skeleton удален');
    }
    
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
            
            console.log('📦 Навигация загружена из кеша');
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
            console.log('💾 Навигация сохранена в кеш');
            
        } catch (error) {
            console.warn('⚠️ Ошибка сохранения кеша навигации:', error);
        }
    }
    
    /**
     * Загрузка навигации с API
     */
    async function fetchNavigationFromAPI() {
        try {
            // Получаем user_id из localStorage для персонализации
            const userData = JSON.parse(localStorage.getItem('telegram_user') || '{}');
            const userId = userData.id || null;
            
            const params = new URLSearchParams();
            if (userId) params.append('user_id', userId);
            params.append('category', 'main');
            
            const response = await fetch(`${CONFIG.API_URL}?${params}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (!data.navigation || !Array.isArray(data.navigation)) {
                throw new Error('Invalid navigation data format');
            }
            
            console.log('🌐 Навигация загружена с API:', data.navigation.length, 'пунктов');
            
            // Кешируем навигацию
            cacheNavigation(data.navigation);
            
            return data.navigation;
            
        } catch (error) {
            console.error('❌ Ошибка загрузки навигации с API:', error);
            throw error;
        }
    }
    
    /**
     * Создание HTML для навигации
     */
    function createNavigationHTML(navigationItems) {
        // Navbar HTML
        const userData = JSON.parse(localStorage.getItem('telegram_user') || '{}');
        const userName = userData.first_name || 'Пользователь';
        const userAvatar = userName.charAt(0).toUpperCase();
        
        const navbarHTML = `
            <nav class="api-navbar">
                <a href="/dashboard/main.html" class="api-navbar-brand">
                    <div class="api-navbar-brand-icon">📱</div>
                    <span>Dialist</span>
                </a>
                
                <div class="api-navbar-user" onclick="toggleApiUserMenu()">
                    <div class="api-navbar-user-avatar">${userAvatar}</div>
                    <div class="api-navbar-user-info">
                        <div class="api-navbar-user-name">${userName}</div>
                        <div class="api-navbar-user-status">Онлайн</div>
                    </div>
                </div>
                
                <div class="api-user-dropdown" id="api-user-dropdown">
                    <div class="api-dropdown-item" onclick="alert('Профиль')">
                        <span>👤</span> Профиль
                    </div>
                    <div class="api-dropdown-item" onclick="alert('Настройки')">
                        <span>⚙️</span> Настройки
                    </div>
                    <div class="api-dropdown-divider"></div>
                    <div class="api-dropdown-item" onclick="confirmLogout()">
                        <span>🚪</span> Выйти
                    </div>
                </div>
            </nav>
        `;
        
        // Sidebar HTML
        let sidebarHTML = `
            <div class="api-sidebar">
                <div class="api-navigation">
        `;
        
        // Генерируем пункты меню
        navigationItems.forEach(item => {
            const isActive = window.location.pathname === item.url ? 'active' : '';
            const badge = item.badge_text ? `<span class="api-nav-badge">${item.badge_text}</span>` : '';
            
            sidebarHTML += `
                <a href="${item.url}" class="api-nav-item ${isActive}" data-page="${item.id}">
                    <span class="api-nav-icon">${item.icon}</span>
                    <span class="api-nav-title">${item.title}</span>
                    ${badge}
                </a>
            `;
            
            // Добавляем дочерние элементы если есть
            if (item.children && item.children.length > 0) {
                item.children.forEach(child => {
                    const childActive = window.location.pathname === child.url ? 'active' : '';
                    const childBadge = child.badge_text ? `<span class="api-nav-badge">${child.badge_text}</span>` : '';
                    
                    sidebarHTML += `
                        <a href="${child.url}" class="api-nav-item api-nav-child ${childActive}" data-page="${child.id}">
                            <span class="api-nav-icon">${child.icon}</span>
                            <span class="api-nav-title">${child.title}</span>
                            ${childBadge}
                        </a>
                    `;
                });
            }
        });
        
        sidebarHTML += `
                </div>
            </div>
        `;
        
        // Main content wrapper
        const mainContentHTML = `
            <div class="api-main-content">
                <div class="api-content-body" id="api-page-content">
                    <!-- Контент страницы будет перемещен сюда -->
                </div>
            </div>
        `;
        
        return {
            navbar: navbarHTML,
            sidebar: sidebarHTML,
            mainContent: mainContentHTML
        };
    }
    
    /**
     * Вставка навигации в DOM
     */
    function insertNavigationIntoDOM(navigationHTML) {
        // Вставляем navbar в начало body
        document.body.insertAdjacentHTML('afterbegin', navigationHTML.navbar);
        
        // Вставляем sidebar после navbar
        document.body.insertAdjacentHTML('beforeend', navigationHTML.sidebar);
        
        // Вставляем main content wrapper
        document.body.insertAdjacentHTML('beforeend', navigationHTML.mainContent);
        
        // Перемещаем существующий контент в main-content
        movePageContentToWrapper();
        
        console.log('✅ API навигация вставлена в DOM');
    }
    
    /**
     * Перемещение контента страницы в wrapper
     */
    function movePageContentToWrapper() {
        const pageContentContainer = document.getElementById('api-page-content');
        if (!pageContentContainer) return;
        
        const elementsToMove = [];
        const bodyChildren = Array.from(document.body.children);
        
        bodyChildren.forEach(child => {
            // Пропускаем навигационные элементы и скрипты
            if (!child.classList.contains('api-navbar') && 
                !child.classList.contains('api-sidebar') &&
                !child.classList.contains('api-main-content') &&
                !child.classList.contains('api-navigation-skeleton') &&
                child.tagName !== 'SCRIPT' &&
                child.tagName !== 'STYLE') {
                elementsToMove.push(child);
            }
        });
        
        // Перемещаем элементы
        elementsToMove.forEach(element => {
            pageContentContainer.appendChild(element);
        });
        
        console.log(`✅ Перемещено ${elementsToMove.length} элементов в page-content`);
    }
    
    /**
     * Fallback навигация
     */
    function createFallbackNavigation() {
        console.log('🔄 Создаем fallback навигацию');
        
        const fallbackItems = [
            {id: 1, title: 'Главная', url: '/dashboard/main.html', icon: '🏠', children: []},
            {id: 2, title: 'Задачи', url: '/dashboard/tasks.html', icon: '📋', children: []},
            {id: 3, title: 'Встречи', url: '/dashboard/meetings.html', icon: '📅', children: []},
            {id: 4, title: 'Проекты', url: '/dashboard/projects.html', icon: '📁', children: []},
            {id: 5, title: 'Покупки', url: '/dashboard/shopping.html', icon: '🛒', children: []},
            {id: 6, title: 'Заметки', url: '/dashboard/notes.html', icon: '📝', children: []},
            {id: 7, title: 'Настройки', url: '/dashboard/settings.html', icon: '⚙️', children: []},
            {id: 8, title: 'UI Kit', url: '/dashboard/ui-kit.html', icon: '🎨', children: []}
        ];
        
        return fallbackItems;
    }
    
    /**
     * Основная функция загрузки навигации
     */
    async function loadNavigation() {
        if (isLoading || isNavigationLoaded) return;
        
        isLoading = true;
        
        try {
            // Создаем skeleton сразу
            createNavigationSkeleton();
            
            let navigationItems = null;
            
            // Пытаемся загрузить из кеша
            navigationItems = getCachedNavigation();
            
            if (!navigationItems) {
                // Загружаем с API с таймаутом
                const timeoutPromise = new Promise((_, reject) => {
                    setTimeout(() => reject(new Error('API timeout')), CONFIG.FALLBACK_TIMEOUT);
                });
                
                try {
                    navigationItems = await Promise.race([
                        fetchNavigationFromAPI(),
                        timeoutPromise
                    ]);
                } catch (apiError) {
                    console.warn('⚠️ API недоступен, используем fallback:', apiError.message);
                    navigationItems = createFallbackNavigation();
                }
            }
            
            // Создаем HTML навигации
            const navigationHTML = createNavigationHTML(navigationItems);
            
            // Вставляем в DOM
            insertNavigationIntoDOM(navigationHTML);
            
            // Ждем немного для плавности и удаляем skeleton
            setTimeout(() => {
                removeNavigationSkeleton();
                isNavigationLoaded = true;
                
                // Уведомляем о готовности навигации
                document.dispatchEvent(new CustomEvent('apiNavigationLoaded', {
                    detail: { navigationItems }
                }));
                
            }, CONFIG.SKELETON_DURATION);
            
        } catch (error) {
            console.error('❌ Критическая ошибка загрузки навигации:', error);
            
            // В крайнем случае показываем минимальную навигацию
            setTimeout(() => {
                removeNavigationSkeleton();
                const fallbackHTML = createNavigationHTML(createFallbackNavigation());
                insertNavigationIntoDOM(fallbackHTML);
            }, 500);
            
        } finally {
            isLoading = false;
        }
    }
    
    /**
     * Глобальные функции для навигации
     */
    window.toggleApiUserMenu = function() {
        const dropdown = document.getElementById('api-user-dropdown');
        if (dropdown) {
            dropdown.classList.toggle('show');
        }
    };
    
    window.confirmLogout = function() {
        if (confirm('Вы уверены, что хотите выйти из системы?')) {
            localStorage.clear();
            window.location.reload();
        }
    };
    
    // Закрытие dropdown при клике вне его
    document.addEventListener('click', function(event) {
        const userButton = event.target.closest('.api-navbar-user');
        const dropdown = document.getElementById('api-user-dropdown');
        
        if (!userButton && dropdown) {
            dropdown.classList.remove('show');
        }
    });
    
    /**
     * Инициализация
     */
    function init() {
        // Проверяем, не загружена ли уже навигация
        if (document.querySelector('.api-navbar') || document.querySelector('.api-sidebar')) {
            console.log('ℹ️ API навигация уже присутствует на странице');
            return;
        }
        
        console.log('🚀 Инициализация API Navigation Loader');
        loadNavigation();
    }
    
    // Автоматический запуск при загрузке DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Экспорт для внешнего использования
    window.ApiNavigationLoader = {
        load: loadNavigation,
        clearCache: () => localStorage.removeItem(CONFIG.CACHE_KEY),
        getCache: getCachedNavigation,
        isLoaded: () => isNavigationLoaded
    };
    
})();