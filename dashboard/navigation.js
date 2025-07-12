// Навигация для Dashboard
class DashboardNavigation {
    constructor() {
        this.currentPage = this.getCurrentPage();
        this.init();
    }

    init() {
        this.createNavigation();
        this.setupEventListeners();
        this.setActivePage();
        this.loadUserInfo();
    }

    getCurrentPage() {
        const path = window.location.pathname;
        const filename = path.split('/').pop();
        
        switch (filename) {
            case 'main.html':
                return 'dashboard';
            case 'tasks.html':
                return 'tasks';
            case 'meetings.html':
                return 'meetings';
            case 'shopping.html':
                return 'shopping';
            case 'settings.html':
                return 'settings';
            default:
                return 'dashboard';
        }
    }

    createNavigation() {
        // Проверяем, есть ли уже navbar на странице
        if (document.querySelector('#main-navbar')) {
            return; // Если navbar уже есть, не создаем новый
        }
        
        // Создаем структуру навигации
        const body = document.body;
        const existingContent = body.innerHTML;
        
        // Создаем navbar как в tasks.html
        body.innerHTML = `
            <!-- Navbar -->
            <nav class="navbar" id="main-navbar">
                <!-- Логотип/Бренд -->
                <a href="/dashboard/main.html" class="navbar-brand">
                    <div class="navbar-brand-icon">📱</div>
                    <span>Dashboard</span>
                </a>
                
                <!-- Центральная область (поиск) - скрывается на мобильных -->
                <div class="navbar-center navbar-mobile-hidden">
                    <div class="navbar-search">
                        <div class="navbar-search-icon">🔍</div>
                        <input type="text" class="navbar-search-input" placeholder="Поиск..." id="navbar-search">
                    </div>
                </div>
                
                <!-- Действия и профиль -->
                <div class="navbar-actions">
                    <!-- Уведомления - скрываются на мобильных -->
                    <button class="navbar-btn navbar-mobile-hidden" title="Уведомления" onclick="showNotifications()">
                        🔔
                        <span class="navbar-btn-badge" id="notifications-badge">0</span>
                    </button>
                    
                    <!-- Сообщения - скрываются на мобильных -->
                    <button class="navbar-btn navbar-mobile-hidden" title="Сообщения" onclick="showMessages()">
                        💬
                        <span class="navbar-btn-badge" id="messages-badge">0</span>
                    </button>
                    
                    <!-- Профиль пользователя - скрывается на мобильных -->
                    <div class="navbar-user navbar-mobile-hidden" onclick="toggleUserDropdown()">
                        <div class="navbar-user-avatar" id="user-avatar">У</div>
                        <div class="navbar-user-info">
                            <div class="navbar-user-name" id="user-name">Пользователь</div>
                            <div class="navbar-user-status" id="user-status">Онлайн</div>
                        </div>
                        <div class="navbar-dropdown" id="user-dropdown">
                            <a href="/dashboard/main.html" class="navbar-dropdown-item">
                                <span class="navbar-dropdown-item-icon">🏠</span>
                                Главная
                            </a>
                            <a href="/dashboard/settings.html" class="navbar-dropdown-item">
                                <span class="navbar-dropdown-item-icon">⚙️</span>
                                Настройки
                            </a>
                            <div class="navbar-dropdown-divider"></div>
                            <a href="/dashboard/ui-kit.html" class="navbar-dropdown-item">
                                <span class="navbar-dropdown-item-icon">🎨</span>
                                UI Kit
                            </a>
                            <div class="navbar-dropdown-divider"></div>
                            <a href="#" class="navbar-dropdown-item" onclick="logout()">
                                <span class="navbar-dropdown-item-icon">🚪</span>
                                Выйти
                            </a>
                        </div>
                    </div>
                    
                    <!-- Мобильное меню (гамбургер) - показывается только на мобильных -->
                    <div class="navbar-mobile-only" onclick="toggleMobileMenu(event)">
                        <button class="mobile-menu-btn" id="mobile-menu-btn">☰</button>
                        
                        <div class="navbar-dropdown" id="mobile-menu-dropdown">
                            <!-- Поиск в мобильном меню -->
                            <div style="padding: 12px;">
                                <div class="navbar-search">
                                    <div class="navbar-search-icon">🔍</div>
                                    <input type="text" class="navbar-search-input" placeholder="Поиск..." id="mobile-search">
                                </div>
                            </div>
                            
                            <div class="navbar-dropdown-divider"></div>
                            
                            <!-- Основные разделы -->
                            <a href="/dashboard/main.html" class="navbar-dropdown-item">
                                <span class="navbar-dropdown-item-icon">🏠</span>
                                Главная
                            </a>
                            <a href="/dashboard/tasks.html" class="navbar-dropdown-item">
                                <span class="navbar-dropdown-item-icon">📋</span>
                                Задачи
                            </a>
                            <a href="/dashboard/meetings.html" class="navbar-dropdown-item">
                                <span class="navbar-dropdown-item-icon">📅</span>
                                Встречи
                            </a>
                            <a href="/dashboard/shopping.html" class="navbar-dropdown-item">
                                <span class="navbar-dropdown-item-icon">🛒</span>
                                Покупки
                            </a>
                            
                            <div class="navbar-dropdown-divider"></div>
                            
                            <!-- Профиль и настройки -->
                            <a href="/dashboard/settings.html" class="navbar-dropdown-item">
                                <span class="navbar-dropdown-item-icon">👤</span>
                                Профиль
                            </a>
                            <a href="/dashboard/settings.html" class="navbar-dropdown-item">
                                <span class="navbar-dropdown-item-icon">⚙️</span>
                                Настройки
                            </a>
                            <a href="/dashboard/ui-kit.html" class="navbar-dropdown-item">
                                <span class="navbar-dropdown-item-icon">🎨</span>
                                UI Kit
                            </a>
                            
                            <div class="navbar-dropdown-divider"></div>
                            
                            <!-- Выход -->
                            <a href="#" class="navbar-dropdown-item" onclick="logout()">
                                <span class="navbar-dropdown-item-icon">🚪</span>
                                Выйти
                            </a>
                        </div>
                    </div>
                </div>
            </nav>

            <div class="dashboard-container" style="max-width: 1200px; margin: 0 auto; padding-top: 70px;">
                ${existingContent}
            </div>
        `;
    }

    getPageTitle() {
        const titles = {
            'dashboard': '🏠 Дашборд',
            'tasks': '📋 Задачи',
            'meetings': '📅 Встречи',
            'shopping': '🛒 Покупки',
            'settings': '⚙️ Настройки'
        };
        return titles[this.currentPage] || '📊 Dashboard';
    }

    setupEventListeners() {
        // Мобильное меню
        const mobileMenuBtn = document.getElementById('mobile-menu-btn');
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebar-overlay');

        if (mobileMenuBtn) {
            mobileMenuBtn.addEventListener('click', () => {
                sidebar.classList.toggle('open');
                overlay.classList.toggle('show');
            });
        }

        if (overlay) {
            overlay.addEventListener('click', () => {
                sidebar.classList.remove('open');
                overlay.classList.remove('show');
            });
        }

        // Закрытие меню при клике на ссылку (мобильная версия)
        document.querySelectorAll('.nav-item').forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth <= 768) {
                    sidebar.classList.remove('open');
                    overlay.classList.remove('show');
                }
            });
        });

        // Обновление счетчиков при загрузке страницы
        this.updateCounters();
    }

    setActivePage() {
        // Устанавливаем активный пункт в мобильном меню
        const mobileMenuItems = document.querySelectorAll('#mobile-menu-dropdown .navbar-dropdown-item');
        
        mobileMenuItems.forEach(item => {
            // Убираем активный стиль со всех пунктов
            item.style.background = '';
            item.style.color = '';
            
            // Проверяем, соответствует ли пункт текущей странице
            const href = item.getAttribute('href');
            if (href) {
                const pageName = href.split('/').pop();
                
                if (pageName === `${this.currentPage}.html`) {
                    // Устанавливаем активный стиль
                    item.style.background = 'rgba(84, 169, 235, 0.2)';
                    item.style.color = 'var(--tg-blue)';
                }
            }
        });
        
        // Обновляем заголовок в navbar-brand
        const navbarBrandText = document.querySelector('.navbar-brand span');
        if (navbarBrandText) {
            const titles = {
                'dashboard': 'Dashboard',
                'tasks': 'Задачи',
                'meetings': 'Встречи',
                'shopping': 'Покупки',
                'settings': 'Настройки'
            };
            
            navbarBrandText.textContent = titles[this.currentPage] || 'Dashboard';
        }
    }

    async loadUserInfo() {
        try {
            const user = Auth.getCurrentUser();
            if (user) {
                const userAvatar = document.getElementById('user-avatar');
                const userName = document.getElementById('user-name');
                
                if (userAvatar && userName) {
                    // Получаем первую букву имени для аватара
                    const firstLetter = user.first_name ? user.first_name.charAt(0).toUpperCase() : '?';
                    userAvatar.textContent = firstLetter;
                    
                    // Отображаем имя пользователя
                    const displayName = user.first_name || user.username || 'Пользователь';
                    userName.textContent = displayName;
                }
            }
        } catch (error) {
            console.error('Ошибка загрузки информации о пользователе:', error);
        }
    }

    async updateCounters() {
        try {
            const user = Auth.getCurrentUser();
            if (!user) return;

            // Загружаем счетчики для разных разделов
            await Promise.all([
                this.updateTasksCounter(user.id),
                this.updateMeetingsCounter(user.id),
                this.updateShoppingCounter(user.id)
            ]);
        } catch (error) {
            console.error('Ошибка обновления счетчиков:', error);
        }
    }

    async updateTasksCounter(userId) {
        try {
            const response = await fetch(`/api/tasks?user_id=${userId}`);
            if (response.ok) {
                const tasks = await response.json();
                const activeTasks = tasks.filter(task => !task.completed);
                const counter = document.getElementById('tasks-count');
                if (counter) {
                    counter.textContent = activeTasks.length;
                    counter.style.display = activeTasks.length > 0 ? 'block' : 'none';
                }
            }
        } catch (error) {
            console.error('Ошибка загрузки счетчика задач:', error);
        }
    }

    async updateMeetingsCounter(userId) {
        try {
            const response = await fetch(`/api/events?user_id=${userId}`);
            if (response.ok) {
                const events = await response.json();
                const upcomingEvents = events.filter(event => {
                    const eventDate = new Date(event.date);
                    const now = new Date();
                    return eventDate >= now;
                });
                const counter = document.getElementById('meetings-count');
                if (counter) {
                    counter.textContent = upcomingEvents.length;
                    counter.style.display = upcomingEvents.length > 0 ? 'block' : 'none';
                }
            }
        } catch (error) {
            console.error('Ошибка загрузки счетчика встреч:', error);
        }
    }

    async updateShoppingCounter(userId) {
        try {
            const response = await fetch(`/api/shopping?user_id=${userId}`);
            if (response.ok) {
                const items = await response.json();
                const activeItems = items.filter(item => !item.completed);
                const counter = document.getElementById('shopping-count');
                if (counter) {
                    counter.textContent = activeItems.length;
                    counter.style.display = activeItems.length > 0 ? 'block' : 'none';
                }
            }
        } catch (error) {
            console.error('Ошибка загрузки счетчика покупок:', error);
        }
    }

    // Метод для добавления кнопок действий в header
    setHeaderActions(actionsHtml) {
        const actionsContainer = document.getElementById('content-header-actions');
        if (actionsContainer) {
            actionsContainer.innerHTML = actionsHtml;
        }
    }
}

// Функция для переключения мобильного меню
function toggleMobileMenu(event) {
    if (event) {
        event.stopPropagation();
    }
    
    const dropdown = document.getElementById('mobile-menu-dropdown');
    const btn = document.getElementById('mobile-menu-btn');
    
    dropdown.classList.toggle('show');
    
    // Изменяем иконку
    if (dropdown.classList.contains('show')) {
        btn.textContent = '✕';
    } else {
        btn.textContent = '☰';
    }
}

// Функция для переключения выпадающего меню пользователя
function toggleUserDropdown() {
    const dropdown = document.getElementById('user-dropdown');
    dropdown.classList.toggle('show');
}

// Закрытие всех выпадающих меню при клике вне них
document.addEventListener('click', function(event) {
    const userDropdown = document.getElementById('user-dropdown');
    const mobileDropdown = document.getElementById('mobile-menu-dropdown');
    const userButton = event.target.closest('.navbar-user');
    const mobileButton = event.target.closest('.navbar-mobile-only');
    
    if (!userButton && userDropdown) {
        userDropdown.classList.remove('show');
    }
    
    if (!mobileButton && mobileDropdown) {
        mobileDropdown.classList.remove('show');
        
        const btn = document.getElementById('mobile-menu-btn');
        if (btn) {
            btn.textContent = '☰';
        }
    }
});

// Инициализация навигации после загрузки DOM
document.addEventListener('DOMContentLoaded', () => {
    // Проверяем, что мы находимся в dashboard
    if (window.location.pathname.includes('/dashboard/')) {
        window.dashboardNav = new DashboardNavigation();
    }
});

// Экспортируем для использования в других скриптах
window.DashboardNavigation = DashboardNavigation;
window.toggleMobileMenu = toggleMobileMenu;
window.toggleUserDropdown = toggleUserDropdown;