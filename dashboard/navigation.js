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
        // Создаем структуру навигации
        const body = document.body;
        const existingContent = body.innerHTML;
        
        body.innerHTML = `
            <div class="dashboard-layout">
                <nav class="sidebar" id="sidebar">
                    <div class="sidebar-header">
                        <h2 class="sidebar-title">
                            <span>📊</span>
                            Dashboard
                        </h2>
                        <p class="sidebar-subtitle">Управление задачами</p>
                    </div>
                    
                    <ul class="nav-menu">
                        <li class="nav-item">
                            <a href="main.html" class="nav-link" data-page="dashboard">
                                <span class="nav-icon">🏠</span>
                                Дашборд
                            </a>
                        </li>
                        <li class="nav-item">
                            <a href="tasks.html" class="nav-link" data-page="tasks">
                                <span class="nav-icon">📋</span>
                                Задачи
                                <span class="nav-badge" id="tasks-count">0</span>
                            </a>
                        </li>
                        <li class="nav-item">
                            <a href="meetings.html" class="nav-link" data-page="meetings">
                                <span class="nav-icon">📅</span>
                                Встречи
                                <span class="nav-badge" id="meetings-count">0</span>
                            </a>
                        </li>
                        <li class="nav-item">
                            <a href="shopping.html" class="nav-link" data-page="shopping">
                                <span class="nav-icon">🛒</span>
                                Покупки
                                <span class="nav-badge" id="shopping-count">0</span>
                            </a>
                        </li>
                        <li class="nav-item">
                            <a href="settings.html" class="nav-link" data-page="settings">
                                <span class="nav-icon">⚙️</span>
                                Настройки
                            </a>
                        </li>
                    </ul>
                    
                    <div class="user-info" id="user-info">
                        <div class="user-avatar" id="user-avatar">?</div>
                        <div class="user-details">
                            <p class="user-name" id="user-name">Загрузка...</p>
                            <p class="user-status">Онлайн</p>
                        </div>
                    </div>
                </nav>
                
                <div class="sidebar-overlay" id="sidebar-overlay"></div>
                
                <main class="main-content">
                    <div class="content-header">
                        <button class="mobile-menu-btn" id="mobile-menu-btn">☰</button>
                        <h1 class="content-title" id="content-title">
                            ${this.getPageTitle()}
                        </h1>
                    </div>
                    <div class="content-body">
                        ${existingContent}
                    </div>
                </main>
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
        document.querySelectorAll('.nav-link').forEach(link => {
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
        // Убираем активный класс со всех ссылок
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });

        // Добавляем активный класс к текущей странице
        const activeLink = document.querySelector(`[data-page="${this.currentPage}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
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
}

// Инициализация навигации после загрузки DOM
document.addEventListener('DOMContentLoaded', () => {
    // Проверяем, что мы находимся в dashboard
    if (window.location.pathname.includes('/dashboard/')) {
        new DashboardNavigation();
    }
});

// Экспортируем для использования в других скриптах
window.DashboardNavigation = DashboardNavigation;