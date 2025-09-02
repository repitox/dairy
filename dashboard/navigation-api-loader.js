// Умный загрузчик навигации на основе API с предотвращением прыжков
(function() {
    'use strict';
    
    // Конфигурация
    const CONFIG = {
        API_URL: '/api/navigation',
        SKELETON_DURATION: 150,
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
    // Кеш отключен — навигация всегда из БД
    function getCachedNavigation() {
        return null;
    }
    
    /**
     * Сохранение навигации в кеш
     */
    // Кеш отключен — не сохраняем навигацию
    function cacheNavigation(navigation) {
        return;
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
            
            // Поддерживаем оба формата ответа:
            // 1) массив элементов
            // 2) объект { navigation: [...] }
            const items = Array.isArray(data) ? data : (data && Array.isArray(data.navigation) ? data.navigation : null);
            if (!items) {
                throw new Error('Invalid navigation data format');
            }
            
            console.log('🌐 Навигация загружена с API:', items.length, 'пунктов');
            
            return items;
            
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
        
        // Генерируем мобильное меню из API данных
        let mobileMenuItems = '';
        navigationItems.forEach(item => {
            mobileMenuItems += `
                <a href="${item.url}" class="navbar-dropdown-item">
                    <span class="navbar-dropdown-item-icon">${item.icon}</span>
                    ${item.title}
                </a>
            `;
        });

        const navbarHTML = `
            <nav class="api-navbar">
                <a href="/dashboard/main.html" class="api-navbar-brand">
                    <div class="api-navbar-brand-icon">📱</div>
                    <span>Dialist</span>
                </a>
                
                <div class="api-navbar-user navbar-mobile-hidden" onclick="toggleApiUserMenu()">
                    <div class="api-navbar-user-avatar">${userAvatar}</div>
                    <div class="api-navbar-user-info">
                        <div class="api-navbar-user-name">${userName}</div>
                        <div class="api-navbar-user-status">Онлайн</div>
                    </div>
                </div>
                
                <div class="api-user-dropdown" id="api-user-dropdown">
                    <div class="api-dropdown-item" onclick="window.location.href='/dashboard/settings.html'">
                        <span>👤</span> Профиль
                    </div>
                    <div class="api-dropdown-item" onclick="confirmLogout()">
                        <span>🚪</span> Выйти
                    </div>
                </div>

                <!-- Мобильное меню (гамбургер) -->
                <div class="navbar-mobile-only" onclick="toggleMobileMenu()">
                    <button class="mobile-menu-btn" id="mobile-menu-btn">☰</button>

                    <div class="navbar-dropdown" id="mobile-menu-dropdown">
                        <!-- Информация о пользователе -->
                        <div class="user-info-mobile" style="padding: 15px; text-align: center;">
                            <div class="navbar-user-avatar" id="mobile-user-avatar"
                                style="margin: 0 auto 10px auto; width: 50px; height: 50px; font-size: 24px;">${userAvatar}</div>
                            <div class="navbar-user-name" id="mobile-user-name"
                                style="font-weight: 600; margin-bottom: 5px;">${userName}</div>
                            <div id="mobile-user-details" style="font-size: 12px; color: var(--text-secondary);">ID: ${userData.id || 0}</div>
                        </div>

                        <div class="navbar-dropdown-divider"></div>

                        <!-- Основные разделы из API -->
                        ${mobileMenuItems}

                        <div class="navbar-dropdown-divider"></div>

                        <!-- Профиль и настройки -->
                        <a href="/dashboard/settings.html" class="navbar-dropdown-item">
                            <span class="navbar-dropdown-item-icon">👤</span>
                            Профиль
                        </a>

                        <!-- Выход -->
                        <a href="#" class="navbar-dropdown-item" onclick="confirmLogout()">
                            <span class="navbar-dropdown-item-icon">🚪</span>
                            Выйти
                        </a>
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
            
            // Всегда грузим из API, без кеша и фоллбеков
            navigationItems = await fetchNavigationFromAPI();
            
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
            
            // Показываем ошибку и убираем скелетон
            setTimeout(() => {
                removeNavigationSkeleton();
                const errorDiv = document.createElement('div');
                errorDiv.style.padding = '16px';
                errorDiv.textContent = 'Не удалось загрузить навигацию';
                document.body.insertAdjacentElement('afterbegin', errorDiv);
            }, 200);
            
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

    // Функции для мобильного меню
    window.toggleMobileMenu = function() {
        const dropdown = document.getElementById('mobile-menu-dropdown');
        const btn = document.getElementById('mobile-menu-btn');
        
        if (dropdown) {
            dropdown.classList.toggle('show');
            if (btn) {
                btn.textContent = dropdown.classList.contains('show') ? '✕' : '☰';
            }
        }
    };
    
    // Закрытие dropdown при клике вне его
    document.addEventListener('click', function(event) {
        const userButton = event.target.closest('.api-navbar-user');
        const mobileButton = event.target.closest('.navbar-mobile-only');
        const dropdown = document.getElementById('api-user-dropdown');
        const mobileDropdown = document.getElementById('mobile-menu-dropdown');
        const mobileBtn = document.getElementById('mobile-menu-btn');
        
        if (!userButton && dropdown) {
            dropdown.classList.remove('show');
        }
        
        if (!mobileButton && mobileDropdown) {
            mobileDropdown.classList.remove('show');
            if (mobileBtn) {
                mobileBtn.textContent = '☰';
            }
        }
    });
    
    /**
     * Инициализация
     */
    function init() {
        // Проверяем, отключена ли навигация для этой страницы
        if (window.__DISABLE_DASHBOARD_NAV__) {
            console.log('🚫 Навигация отключена для этой страницы');
            return;
        }
        
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
        clearCache: () => {},
        getCache: () => null,
        isLoaded: () => isNavigationLoaded
    };
    
})();