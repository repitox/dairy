/**
 * Утилиты для работы с авторизацией в Dashboard
 */

// Получение данных текущего пользователя
function getCurrentUser() {
    try {
        const savedUser = localStorage.getItem("telegram_user");
        if (!savedUser) {
            return null;
        }
        
        const user = JSON.parse(savedUser);
        
        // Проверяем валидность данных
        if (!user.id || !user.first_name) {
            console.error("❌ Некорректные данные пользователя");
            localStorage.removeItem("telegram_user");
            return null;
        }
        
        return user;
    } catch (e) {
        console.error("❌ Ошибка получения данных пользователя:", e);
        localStorage.removeItem("telegram_user");
        return null;
    }
}

// Получение ID текущего пользователя
function getCurrentUserId() {
    const user = getCurrentUser();
    return user ? user.id : null;
}

// Проверка авторизации
function isAuthenticated() {
    return getCurrentUser() !== null;
}

// Выход из системы
function logout() {
    localStorage.removeItem("telegram_user");
    localStorage.removeItem("user_id"); // На всякий случай
    window.location.href = '/dashboard/index.html';
}

// Перенаправление на авторизацию если не авторизован
function requireAuth() {
    if (!isAuthenticated()) {
        console.log("🔄 Требуется авторизация, перенаправление...");
        window.location.href = '/dashboard/index.html';
        return false;
    }
    return true;
}

// Безопасный API запрос с автоматической подстановкой user_id
async function apiRequest(url, options = {}) {
    const userId = getCurrentUserId();
    if (!userId) {
        throw new Error('Пользователь не авторизован');
    }
    
    // Добавляем user_id в URL если его там нет
    const urlObj = new URL(url, window.location.origin);
    if (!urlObj.searchParams.has('user_id')) {
        urlObj.searchParams.set('user_id', userId);
    }
    
    // Устанавливаем заголовки по умолчанию
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    };
    
    try {
        const response = await fetch(urlObj.toString(), defaultOptions);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return response;
    } catch (error) {
        console.error('❌ Ошибка API запроса:', error);
        throw error;
    }
}

// Инициализация страницы с проверкой авторизации
function initAuthenticatedPage() {
    document.addEventListener("DOMContentLoaded", () => {
        if (!requireAuth()) {
            return;
        }
        
        const user = getCurrentUser();
        console.log("✅ Пользователь загружен:", user.first_name);
        
        // Очищаем URL от параметров (если есть старые ссылки)
        if (window.location.search) {
            const cleanUrl = window.location.pathname;
            window.history.replaceState({}, document.title, cleanUrl);
        }
        
        // Вызываем callback если передан
        if (typeof window.onUserLoaded === 'function') {
            window.onUserLoaded(user);
        }
    });
}

// Экспортируем функции в глобальную область
window.Auth = {
    getCurrentUser,
    getCurrentUserId,
    isAuthenticated,
    logout,
    requireAuth,
    apiRequest,
    initAuthenticatedPage
};