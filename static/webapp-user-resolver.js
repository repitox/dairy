/**
 * Утилита для преобразования telegram_id в внутренний user_id
 */

let cachedUserId = null;

/**
 * Получить внутренний user_id по telegram_id
 * @returns {Promise<number>} Внутренний user_id
 */
async function getUserId() {
    // Если уже кешировали, возвращаем кешированное значение
    if (cachedUserId !== null) {
        return cachedUserId;
    }

    try {
        // Получаем telegram_id из WebApp или используем тестовый
        const tg = window.Telegram?.WebApp;
        const telegramId = tg?.initDataUnsafe?.user?.id || "123456789";
        
        // Преобразуем telegram_id в внутренний user_id
        const response = await fetch(`/api/user/resolve?telegram_id=${telegramId}`);
        if (!response.ok) {
            throw new Error(`Пользователь не найден: ${response.status}`);
        }
        
        const data = await response.json();
        cachedUserId = data.user_id;
        
        console.log(`✅ Resolved telegram_id ${telegramId} to user_id ${cachedUserId}`);
        return cachedUserId;
        
    } catch (error) {
        console.error('❌ Ошибка получения user_id:', error);
        throw error;
    }
}

/**
 * Сбросить кеш user_id (для тестирования)
 */
function clearUserIdCache() {
    cachedUserId = null;
}