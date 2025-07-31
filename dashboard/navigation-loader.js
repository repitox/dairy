// Загрузчик навигационного компонента с предотвращением "прыгания"
(function() {
    // Подключаем skeleton CSS если его нет
    function ensureSkeletonCSS() {
        if (document.querySelector('link[href*="navigation-skeleton.css"]')) {
            return Promise.resolve();
        }
        
        return new Promise((resolve) => {
            const skeletonCSS = document.createElement('link');
            skeletonCSS.rel = 'stylesheet';
            skeletonCSS.href = '/dashboard/navigation-skeleton.css';
            skeletonCSS.onload = () => {
                console.log('🔮 Skeleton CSS загружен');
                resolve();
            };
            
            const navigationCSS = document.querySelector('link[href*="navigation.css"]');
            if (navigationCSS) {
                navigationCSS.parentNode.insertBefore(skeletonCSS, navigationCSS.nextSibling);
            } else {
                document.head.appendChild(skeletonCSS);
            }
        });
    }
    
    // Создаем skeleton сразу при загрузке скрипта
    function createNavigationSkeleton() {
        // Navbar skeleton
        const navbarSkeleton = document.createElement('div');
        navbarSkeleton.className = 'navigation-skeleton';
        document.body.insertAdjacentElement('afterbegin', navbarSkeleton);
        
        // Sidebar skeleton
        const sidebarSkeleton = document.createElement('div');
        sidebarSkeleton.className = 'sidebar-skeleton';
        
        // Создаем контейнер навигации как в реальном sidebar
        const navigationDemo = document.createElement('div');
        navigationDemo.style.cssText = 'padding: 0 15px;';
        
        // Добавляем skeleton элементы меню (8 пунктов как в реальном меню)
        const menuItems = [
            '🏠 Главная', '📋 Задачи', '📅 Встречи', '📁 Проекты', 
            '🛒 Покупки', '📝 Заметки', '⚙️ Настройки', '🎨 UI Kit'
        ];
        
        menuItems.forEach((item, index) => {
            const skeletonItem = document.createElement('div');
            skeletonItem.style.cssText = `
                display: flex;
                align-items: center;
                padding: 12px 16px;
                height: 44px;
                background: linear-gradient(90deg, 
                    rgba(255, 255, 255, 0.05) 25%, 
                    rgba(255, 255, 255, 0.08) 50%, 
                    rgba(255, 255, 255, 0.05) 75%
                );
                background-size: 200% 100%;
                animation: skeleton-shimmer 1.5s infinite;
                animation-delay: ${index * 0.1}s;
                border-radius: 12px;
                margin-bottom: 4px;
                color: transparent;
                font-size: 14px;
                user-select: none;
            `;
            skeletonItem.textContent = item;
            navigationDemo.appendChild(skeletonItem);
        });
        
        sidebarSkeleton.appendChild(navigationDemo);
        
        document.body.appendChild(sidebarSkeleton);
        
        console.log('🔮 Navigation skeleton создан');
    }
    
    // Функция для загрузки навигации
    async function loadNavigation() {
        try {
            // Добавляем класс загрузки
            document.body.classList.add('navigation-loading');
            
            const response = await fetch('/dashboard/navigation-component.html');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const html = await response.text();
            
            // Создаем временный контейнер для парсинга HTML
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;
            
            // Извлекаем навигацию и скрипт
            const navbar = tempDiv.querySelector('nav');
            const dashboardLayout = tempDiv.querySelector('.dashboard-layout');
            const scriptContent = html.match(/<script>([\s\S]*?)<\/script>/);
            
            // Вставляем навигацию в начало body
            if (navbar) {
                document.body.insertAdjacentHTML('afterbegin', navbar.outerHTML);
            }
            if (dashboardLayout) {
                document.body.insertAdjacentHTML('beforeend', dashboardLayout.outerHTML);
            }
            
            // Выполняем скрипт
            if (scriptContent && scriptContent[1]) {
                const script = document.createElement('script');
                script.textContent = scriptContent[1];
                document.head.appendChild(script);
            }
            
            console.log('✅ Навигация загружена успешно');
            
            // Плавно скрываем skeleton и показываем настоящую навигацию
            setTimeout(() => {
                // Добавляем класс загруженной навигации
                document.body.classList.add('navigation-loaded');
                document.body.classList.remove('navigation-loading');
                
                // Уведомляем о том, что навигация загружена и готова
                document.dispatchEvent(new CustomEvent('navigationLoaded'));
                console.log('✅ Skeleton скрыт, навигация активна');
            }, 150); // Даем время для рендеринга
            
        } catch (error) {
            console.error('❌ Ошибка загрузки навигации:', error);
            
            // Fallback - показываем простую навигацию
            showFallbackNavigation();
        }
    }
    
    // Fallback навигация на случай ошибки
    function showFallbackNavigation() {
        const fallbackNav = `
            <nav style="background: var(--glass-medium); padding: 10px; margin-bottom: 20px; border-radius: 8px;">
                <div style="display: flex; gap: 15px; align-items: center;">
                    <a href="/dashboard/main.html" style="color: var(--text-primary); text-decoration: none;">🏠 Главная</a>
                    <a href="/dashboard/tasks.html" style="color: var(--text-primary); text-decoration: none;">📋 Задачи</a>
                    <a href="/dashboard/meetings.html" style="color: var(--text-primary); text-decoration: none;">📅 Встречи</a>
                    <a href="/dashboard/shopping.html" style="color: var(--text-primary); text-decoration: none;">🛒 Покупки</a>
                    <a href="/dashboard/notes.html" style="color: var(--text-primary); text-decoration: none;">📝 Заметки</a>
                    <a href="/dashboard/settings.html" style="color: var(--text-primary); text-decoration: none;">⚙️ Настройки</a>
                </div>
            </nav>
        `;
        document.body.insertAdjacentHTML('afterbegin', fallbackNav);
    }
    
    // Функция для обертывания контента страницы
    function wrapPageContent() {
        const pageContentContainer = document.getElementById('page-content');
        if (!pageContentContainer) {
            console.warn('Контейнер page-content не найден');
            return;
        }

        // Собираем все элементы, которые нужно переместить
        const elementsToMove = [];
        const bodyChildren = Array.from(document.body.children);
        
        bodyChildren.forEach(child => {
            // Пропускаем навигационные элементы и скрипты
            if (!child.classList.contains('navbar') && 
                !child.classList.contains('dashboard-layout') &&
                child.tagName !== 'SCRIPT' &&
                child.id !== 'page-content') {
                elementsToMove.push(child);
            }
        });

        // Перемещаем элементы в контейнер
        elementsToMove.forEach(element => {
            pageContentContainer.appendChild(element);
        });

        console.log(`✅ Перемещено ${elementsToMove.length} элементов в page-content`);
    }
    
    // Инициализация
    async function init() {
        // Проверяем, не загружена ли уже навигация
        if (document.querySelector('.navbar') || document.querySelector('.dashboard-layout')) {
            console.log('ℹ️ Навигация уже присутствует на странице');
            return;
        }
        
        // Сначала подключаем skeleton CSS
        await ensureSkeletonCSS();
        
        // Затем создаем skeleton
        createNavigationSkeleton();
        
        // И загружаем навигацию
        loadNavigation().then(() => {
            // После загрузки навигации оборачиваем контент
            setTimeout(wrapPageContent, 100);
        });
    }
    
    // Запускаем инициализацию
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Экспортируем функции для внешнего использования
    window.NavigationLoader = {
        loadNavigation: loadNavigation,
        wrapPageContent: wrapPageContent
    };
})();