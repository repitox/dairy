/**
 * Модуль проверки регистрации пользователя для WebApp
 */

// Проверка регистрации пользователя
async function checkUserRegistration(userId) {
    try {
        console.log(`🔍 Отправляем запрос: GET /api/users/${userId}`);
        const response = await fetch(`/api/users/${userId}`);
        console.log(`📡 Ответ сервера: status=${response.status}`);
        
        if (response.status === 404) {
            // Пользователь не найден - показываем экран регистрации
            console.log('❌ Пользователь не найден (404)');
            return false;
        } else if (response.ok) {
            // Пользователь найден - можно загружать данные
            const userData = await response.json();
            console.log('✅ Пользователь найден:', userData);
            return true;
        } else {
            // Другая ошибка - показываем экран регистрации для безопасности
            console.error('❌ Ошибка проверки пользователя:', response.status);
            const errorText = await response.text();
            console.error('Текст ошибки:', errorText);
            return false;
        }
    } catch (error) {
        console.error('❌ Ошибка запроса проверки пользователя:', error);
        // При ошибке сети показываем экран регистрации
        return false;
    }
}

// Показать экран регистрации
function showRegistrationScreen() {
    // Создаем экран регистрации если его нет
    let registrationScreen = document.getElementById('registration-screen');
    if (!registrationScreen) {
        registrationScreen = createRegistrationScreen();
        document.body.appendChild(registrationScreen);
    }
    
    registrationScreen.classList.remove('hidden');
    
    // Скрываем основной контент
    const mainContent = document.getElementById('main-content') || 
                       document.querySelector('.webapp-container > :not(#registration-screen)');
    if (mainContent) {
        mainContent.classList.add('hidden');
    }
    
    // Скрываем навигацию настроек
    const navigation = document.querySelector('.dashboard-navigation');
    if (navigation) {
        navigation.classList.add('hidden');
    }
}

// Показать основной контент
function showMainContent() {
    const registrationScreen = document.getElementById('registration-screen');
    if (registrationScreen) {
        registrationScreen.classList.add('hidden');
    }
    
    // Показываем основной контент
    const mainContent = document.getElementById('main-content') || 
                       document.querySelector('.webapp-container > :not(#registration-screen)');
    if (mainContent) {
        mainContent.classList.remove('hidden');
    }
    
    // Показываем навигацию настроек для авторизованных пользователей
    const navigation = document.querySelector('.dashboard-navigation');
    if (navigation) {
        navigation.classList.remove('hidden');
    }
}

// Создать экран регистрации
function createRegistrationScreen() {
    const screen = document.createElement('div');
    screen.id = 'registration-screen';
    screen.className = 'registration-screen hidden';
    
    screen.innerHTML = `
        <div class="registration-icon">🚀</div>
        <h1 class="registration-title">Добро пожаловать!</h1>
        <p class="registration-message">
            Для работы с Task Manager необходимо пройти регистрацию. 
            Отправьте команду боту в Telegram, чтобы начать использовать все возможности приложения.
        </p>
        <div class="registration-command">/start</div>
        <div class="registration-steps">
            <h4>📋 Как начать работу:</h4>
            <ol>
                <li>Закройте это окно</li>
                <li>Вернитесь в чат с ботом</li>
                <li>Отправьте команду <strong>/start</strong></li>
                <li>Следуйте инструкциям бота</li>
                <li>Откройте WebApp снова</li>
            </ol>
        </div>
    `;
    
    return screen;
}

// Добавить стили для экрана регистрации
function addRegistrationStyles() {
    const existingStyles = document.getElementById('registration-styles');
    if (existingStyles) return;
    
    const style = document.createElement('style');
    style.id = 'registration-styles';
    style.textContent = `
        /* Экран регистрации */
        .registration-screen {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 60vh;
            text-align: center;
            padding: 40px 20px;
        }

        .registration-icon {
            font-size: 64px;
            margin-bottom: 20px;
            opacity: 0.8;
        }

        .registration-title {
            font-size: 24px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 15px;
        }

        .registration-message {
            font-size: 16px;
            color: var(--text-secondary);
            line-height: 1.6;
            margin-bottom: 30px;
            max-width: 400px;
        }

        .registration-command {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 15px 20px;
            font-family: 'Courier New', monospace;
            font-size: 18px;
            font-weight: 600;
            color: var(--bg-accent);
            margin-bottom: 20px;
            letter-spacing: 1px;
        }

        .registration-steps {
            text-align: left;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 20px;
            margin-top: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .registration-steps h4 {
            color: var(--text-primary);
            margin-bottom: 15px;
            font-size: 16px;
        }

        .registration-steps ol {
            color: var(--text-secondary);
            padding-left: 20px;
            line-height: 1.8;
        }

        .registration-steps li {
            margin-bottom: 8px;
        }

        .hidden {
            display: none !important;
        }
    `;
    
    document.head.appendChild(style);
}

// Инициализация проверки регистрации
async function initAuthCheck(onSuccess, onFailure) {
    try {
        // Добавляем стили
        addRegistrationStyles();
        
        // Получаем ID пользователя
        console.log("Telegram WebApp объект:", window.Telegram?.WebApp);
        console.log("initDataUnsafe:", window.Telegram?.WebApp?.initDataUnsafe);
        console.log("user данные:", window.Telegram?.WebApp?.initDataUnsafe?.user);
        
        let userId = window.Telegram?.WebApp?.initDataUnsafe?.user?.id;
        console.log("Получен userId из Telegram:", userId);
        
        // Режим отладки - если в URL есть debug_user_id, используем его
        const urlParams = new URLSearchParams(window.location.search);
        const debugUserId = urlParams.get('debug_user_id');
        const skipAuth = urlParams.get('skip_auth');
        
        if (skipAuth === 'true') {
            console.log("🔧 Режим отладки: пропускаем проверку авторизации");
            showMainContent();
            if (onSuccess) onSuccess(userId || 'debug');
            return;
        }
        
        if (debugUserId) {
            userId = parseInt(debugUserId);
            console.log("🔧 Режим отладки: используем debug_user_id =", userId);
        }
        
        if (!userId) {
            console.warn("Не удалось получить Telegram User ID, показываем экран регистрации");
            showRegistrationScreen();
            if (onFailure) onFailure();
            return;
        }
        
        console.log("Проверяем регистрацию пользователя:", userId);
        
        // Проверяем регистрацию пользователя
        const isRegistered = await checkUserRegistration(userId);
        
        if (isRegistered) {
            // Пользователь зарегистрирован - показываем основной контент
            console.log("Пользователь зарегистрирован");
            showMainContent();
            if (onSuccess) onSuccess(userId);
        } else {
            // Пользователь не зарегистрирован - показываем экран регистрации
            console.log("Пользователь не зарегистрирован, показываем экран регистрации");
            showRegistrationScreen();
            if (onFailure) onFailure();
        }
    } catch (error) {
        console.error("Ошибка проверки регистрации:", error);
        // При ошибке показываем экран регистрации для безопасности
        showRegistrationScreen();
        if (onFailure) onFailure();
    }
}

// Экспорт функций для использования в других файлах
window.AuthCheck = {
    checkUserRegistration,
    showRegistrationScreen,
    showMainContent,
    initAuthCheck
};