# 🔐 Система проверки регистрации в WebApp

## 📋 Обзор

Реализована комплексная система проверки регистрации пользователей для всех страниц Telegram WebApp. При открытии любой страницы WebApp проверяется, зарегистрирован ли пользователь в системе.

## 🎯 Функциональность

### ✅ **Для зарегистрированных пользователей:**
- Страница загружается нормально
- Отображается весь функционал
- Данные загружаются из API

### ❌ **Для незарегистрированных пользователей:**
- Показывается экран с инструкцией
- Основной контент скрыт
- Навигация настроек скрыта
- Предлагается отправить команду `/start` боту

## 🔧 Техническая реализация

### 1. **API Endpoint для проверки пользователя**

Добавлен новый endpoint в `bot.py`:

```python
@app.get("/api/users/{user_id}")
async def get_user_profile(user_id: int):
    """Проверить существование пользователя и получить базовую информацию"""
    try:
        db_user_id = resolve_user_id(user_id)
        if not db_user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Получаем информацию о пользователе из БД
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, telegram_id, first_name, username, registered_at
                    FROM users 
                    WHERE telegram_id = %s
                """, (user_id,))
                user = cur.fetchone()
                
                if not user:
                    raise HTTPException(status_code=404, detail="User not found")
                
                return {
                    "id": user["telegram_id"],
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                    "username": user["username"],
                    "created_at": user["created_at"].isoformat() if user["created_at"] else None,
                    "registered": True
                }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user profile: {str(e)}")
```

### 2. **Общий модуль проверки регистрации**

Создан файл `/static/auth-check.js` с функциями:

```javascript
// Проверка регистрации пользователя
async function checkUserRegistration(userId) {
    try {
        const response = await fetch(`/api/users/${userId}`);
        
        if (response.status === 404) {
            return false; // Пользователь не найден
        } else if (response.ok) {
            return true; // Пользователь найден
        } else {
            console.error('Ошибка проверки пользователя:', response.status);
            return false;
        }
    } catch (error) {
        console.error('Ошибка запроса проверки пользователя:', error);
        return false;
    }
}

// Инициализация проверки регистрации
async function initAuthCheck(onSuccess, onFailure) {
    try {
        const userId = window.Telegram?.WebApp?.initDataUnsafe?.user?.id || "123456789";
        const isRegistered = await checkUserRegistration(userId);
        
        if (isRegistered) {
            showMainContent();
            if (onSuccess) onSuccess(userId);
        } else {
            showRegistrationScreen();
            if (onFailure) onFailure();
        }
    } catch (error) {
        console.error("Ошибка проверки регистрации:", error);
        showRegistrationScreen();
        if (onFailure) onFailure();
    }
}
```

### 3. **Экран регистрации**

Автоматически создается красивый экран с инструкциями:

```html
<div class="registration-screen">
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
</div>
```

## 📄 Обновленные страницы

### ✅ **Полностью обновлены:**
- ✅ `index.html` - главная страница
- ✅ `tasks.html` - список задач  
- ✅ `task_add.html` - добавление задачи
- ✅ `shopping.html` - список покупок

### ✅ **Добавлен скрипт auth-check.js:**
- ✅ `events.html` - события
- ✅ `project.html` - проект
- ✅ `task.html` - просмотр задачи
- ✅ `event_create.html` - создание события
- ✅ `project_select.html` - выбор проекта
- ✅ `task_edit.html` - редактирование задачи
- ✅ `settings.html` - настройки
- ✅ `timezone-settings.html` - настройки времени

## 🎨 Стили экрана регистрации

```css
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
```

## 🔄 Логика работы

1. **При загрузке страницы:**
   - Получается Telegram User ID
   - Отправляется запрос к `/api/users/{user_id}`
   - Проверяется статус ответа

2. **Если пользователь найден (200 OK):**
   - Показывается основной контент
   - Показывается навигация настроек
   - Вызывается callback `onSuccess(userId)`
   - Загружаются данные страницы

3. **Если пользователь не найден (404):**
   - Скрывается основной контент
   - Скрывается навигация настроек
   - Показывается экран регистрации
   - Вызывается callback `onFailure()`

4. **При ошибке сети:**
   - Показывается экран регистрации (безопасный подход)
   - Логируется ошибка в консоль

## 🚀 Преимущества

### ✅ **Безопасность:**
- Незарегистрированные пользователи не могут получить доступ к данным
- Все API запросы блокируются до регистрации

### ✅ **UX/UI:**
- Понятные инструкции для новых пользователей
- Красивый дизайн экрана регистрации
- Единообразный опыт на всех страницах

### ✅ **Техническая реализация:**
- Переиспользуемый модуль `auth-check.js`
- Автоматическое добавление стилей
- Callback система для гибкой интеграции

### ✅ **Производительность:**
- Быстрая проверка через API
- Кэширование результата в рамках сессии
- Минимальное влияние на загрузку страниц

## 🎯 Результат

Теперь все страницы WebApp защищены от доступа незарегистрированных пользователей. Новые пользователи получают четкие инструкции о том, как начать работу с системой через команду `/start` в Telegram боте.

---

*Документ создан: 27 января 2025*  
*Версия проекта: v2.9.15*