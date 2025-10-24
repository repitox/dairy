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

// Получение ID текущего пользователя (ID из колонки id таблицы users)
function getCurrentUserId() {
    const user = getCurrentUser();
    
    if (user) {
        const telegramId = user.telegram_id ? ` (Telegram ID: ${user.telegram_id})` : '';
        console.log(`✅ Используем database ID пользователя: ${user.id}${telegramId}`);
        return user.id;
    }
    
    console.log('❌ Пользователь не найден');
    return null;
}

// Проверка авторизации
function isAuthenticated() {
    return getCurrentUser() !== null;
}

// Выход из системы
function logout() {
    try {
        // Очищаем все данные авторизации
        localStorage.removeItem("telegram_user");
        localStorage.removeItem("user_id");
        localStorage.removeItem("user_auth");
        
        // Очищаем все остальные данные пользователя
        Object.keys(localStorage).forEach(key => {
            if (key.startsWith('user_') || key.startsWith('telegram_')) {
                localStorage.removeItem(key);
            }
        });
        
        console.log('✅ Выход выполнен, данные очищены');
        window.location.href = '/dashboard/';
    } catch (error) {
        console.error('❌ Ошибка при выходе:', error);
        window.location.href = '/dashboard/';
    }
}

// Перенаправление на авторизацию если не авторизован
function requireAuth() {
    if (!isAuthenticated()) {
        console.log("🔄 Требуется авторизация, перенаправление на index.html");
        // Используем setTimeout чтобы убедиться, что это выполнится в конце очереди событий
        setTimeout(() => {
            window.location.href = '/dashboard/index.html';
        }, 0);
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

// Валидация пользователя на сервере
async function validateUserOnServer() {
    const user = getCurrentUser();
    if (!user) {
        return false;
    }

    try {
        console.log('🔍 Проверяем пользователя на сервере...');
        // Используем правильный user_id (внутренний ID из БД)
        const response = await fetch(`/api/user/validate?user_id=${user.id}`);
        
        if (!response.ok) {
            console.log('❌ Валидация не прошла:', response.status);
            logout();
            return false;
        }
        
        const result = await response.json();
        
        if (!result.valid) {
            console.log('❌ Пользователь не валиден на сервере');
            logout();
            return false;
        }
        
        // Если в localStorage старая структура - обновляем на новую
        if (result.id && (user.id !== result.id || !user.telegram_id)) {
            console.log('🔄 Мигрируем localStorage на новую структуру ID');
            console.log('Старая структура:', { id: user.id, internal_id: user.internal_id });
            console.log('Новая структура:', { id: result.id, telegram_id: result.telegram_id });
            
            // Сохраняем telegram_id если его еще нет
            if (!user.telegram_id && user.id > 1000000) {
                user.telegram_id = user.id; // Старый id был telegram_id
            }
            
            // Обновляем на правильный ID из БД
            user.id = result.id;
            user.personal_project_id = result.personal_project_id;
            
            // Удаляем старое поле internal_id если оно есть
            delete user.internal_id;
            
            localStorage.setItem("telegram_user", JSON.stringify(user));
            console.log('✅ Миграция завершена, новая структура:', user);
            
            // Принудительно перезагружаем страницу для применения изменений
            console.log('🔄 Перезагружаем страницу для применения новой структуры...');
            window.location.reload();
        }
        
        console.log('✅ Пользователь валиден на сервере');
        return true;
        
    } catch (error) {
        console.error('❌ Ошибка валидации пользователя:', error);
        logout();
        return false;
    }
}

// Функция для ожидания загрузки необходимых модулей
async function waitForRequiredModules() {
    const maxWaitTime = 5000; // 5 секунд максимум
    const startTime = Date.now();
    
    // Список проверяемых модулей
    const requiredModules = ['DateTimeUtils'];
    
    while (Date.now() - startTime < maxWaitTime) {
        let allLoaded = true;
        
        for (const module of requiredModules) {
            if (!window[module]) {
                allLoaded = false;
                break;
            }
        }
        
        if (allLoaded) {
            console.log('✅ Все необходимые модули загружены');
            return true;
        }
        
        // Ждем 100ms перед следующей проверкой
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    console.warn('⚠️ Некоторые модули не загружены в отведенное время');
    return false;
}

// Инициализация страницы с проверкой авторизации
function initAuthenticatedPage() {
    // Сначала проверим авторизацию синхронно
    if (!isAuthenticated()) {
        console.log("🔄 Не авторизован, перенаправление на index.html");
        window.location.href = '/dashboard/index.html';
        return; // Остановить выполнение
    }

    // Получаем пользователя
    const user = getCurrentUser();
    if (!user) {
        console.log("❌ Ошибка: пользователь не найден в localStorage");
        window.location.href = '/dashboard/index.html';
        return;
    }

    console.log("✅ Пользователь авторизован:", user.first_name);

    // Если DOM уже готов - вызываем callback сразу
    if (document.readyState === 'loading') {
        console.log('⏳ DOM еще загружается, ждем DOMContentLoaded');
        document.addEventListener('DOMContentLoaded', () => {
            if (typeof window.onUserLoaded === 'function') {
                console.log('🎯 Вызываем onUserLoaded callback');
                window.onUserLoaded(user);
            } else {
                console.warn('⚠️ window.onUserLoaded не определен как функция');
            }
        }, { once: true });
    } else {
        console.log('✅ DOM уже готов, вызываем callback сразу');
        if (typeof window.onUserLoaded === 'function') {
            console.log('🎯 Вызываем onUserLoaded callback');
            window.onUserLoaded(user);
        } else {
            console.warn('⚠️ window.onUserLoaded не определен как функция');
        }
    }
}

// Очередь для отложенной инициализации
let initQueue = [];
let authReady = false;

// Функция для безопасного вызова initAuthenticatedPage с поддержкой деferred вызовов
function safeInitAuthenticatedPage() {
    if (authReady) {
        return initAuthenticatedPage();
    } else {
        // Если Auth еще не готов, добавляем в очередь
        initQueue.push(initAuthenticatedPage);
    }
}

// Экспортируем функции в глобальную область
window.Auth = {
    getCurrentUser,
    getCurrentUserId,
    isAuthenticated,
    logout,
    requireAuth,
    apiRequest,
    initAuthenticatedPage: safeInitAuthenticatedPage,
    validateUserOnServer
};

// Отмечаем auth как готов и обрабатываем очередь
authReady = true;
while (initQueue.length > 0) {
    const fn = initQueue.shift();
    fn();
}