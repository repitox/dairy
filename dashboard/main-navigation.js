// Упрощенная навигация для главной страницы Dashboard
class MainPageNavigation {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Мобильное меню
        const mobileMenuBtn = document.getElementById('mobile-menu-btn');
        const mobileMenuDropdown = document.getElementById('mobile-menu-dropdown');
        
        if (mobileMenuBtn && mobileMenuDropdown) {
            mobileMenuBtn.addEventListener('click', (event) => {
                event.stopPropagation(); // Предотвращаем всплытие события
                mobileMenuDropdown.classList.toggle('show');
                mobileMenuBtn.textContent = mobileMenuDropdown.classList.contains('show') ? '✕' : '☰';
            });
            
            // Закрытие меню при клике вне его
            document.addEventListener('click', (event) => {
                if (!mobileMenuBtn.contains(event.target) && !mobileMenuDropdown.contains(event.target)) {
                    mobileMenuDropdown.classList.remove('show');
                    mobileMenuBtn.textContent = '☰';
                }
            });
        }
        
        // Обработка выпадающего меню пользователя
        const userDropdownToggle = document.querySelector('.navbar-user');
        const userDropdown = document.getElementById('user-dropdown');
        
        if (userDropdownToggle && userDropdown) {
            userDropdownToggle.addEventListener('click', (event) => {
                event.stopPropagation();
                userDropdown.classList.toggle('show');
            });
            
            // Закрытие меню при клике вне его
            document.addEventListener('click', (event) => {
                if (!userDropdownToggle.contains(event.target)) {
                    userDropdown.classList.remove('show');
                }
            });
        }
    }
}

// Инициализация навигации после загрузки DOM
document.addEventListener('DOMContentLoaded', () => {
    window.mainNav = new MainPageNavigation();
});