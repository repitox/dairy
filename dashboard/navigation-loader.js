// Загрузчик навигационного компонента
(function() {
    // Функция для загрузки навигации
    async function loadNavigation() {
        try {
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
            
            // Ждем немного, чтобы скрипт выполнился
            setTimeout(() => {
                // Уведомляем о том, что навигация загружена и готова
                document.dispatchEvent(new CustomEvent('navigationLoaded'));
                console.log('✅ Событие navigationLoaded отправлено');
            }, 50);
            
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
    function init() {
        // Проверяем, не загружена ли уже навигация
        if (document.querySelector('.navbar') || document.querySelector('.dashboard-layout')) {
            console.log('ℹ️ Навигация уже присутствует на странице');
            return;
        }
        
        // Загружаем навигацию
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