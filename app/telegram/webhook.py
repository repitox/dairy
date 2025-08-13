"""
Webhook для Telegram
"""
import json
from datetime import datetime
from fastapi import Request
from telegram import Update

from app.core.config import settings


def setup_webhook(app, telegram_app):
    """Настройка webhook для Telegram"""
    
    @app.post(settings.WEBHOOK_PATH)
    async def telegram_webhook(req: Request):
        try:
            data = await req.json()
            
            # Записываем данные webhook в файл для отладки
            with open("/tmp/webhook_debug.log", "a") as f:
                f.write(f"=== {datetime.utcnow().isoformat()} ===\n")
                f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n\n")
            
            print("📩 Webhook получен:", data.get("message", {}).get("text", data))
            
            # Логируем информацию о пользователе
            if "message" in data and "from" in data["message"]:
                user = data["message"]["from"]
                print(f"👤 От пользователя: ID={user['id']}, username={user.get('username', 'None')}")
            
            update = Update.de_json(data, telegram_app.bot)
            print(f"🔄 Обрабатываем update: {update.update_id}")
            
            await telegram_app.process_update(update)
            print("✅ Update обработан успешно")
            
            return {"status": "ok"}
        except Exception as e:
            print(f"❌ Ошибка в webhook: {e}")
            import traceback
            traceback.print_exc()
            
            # Записываем ошибку в файл
            with open("/tmp/webhook_debug.log", "a") as f:
                f.write(f"ERROR {datetime.utcnow().isoformat()}: {e}\n")
                f.write(traceback.format_exc() + "\n\n")
                
            return {"status": "error", "message": str(e)}
    
    # Тестовые маршруты для отладки
    @app.get("/webhook-info")
    async def webhook_info():
        """Информация о настройке webhook"""
        return {
            "webhook_url": settings.WEBHOOK_URL,
            "webhook_path": settings.WEBHOOK_PATH,
            "domain": settings.DOMAIN,
            "token_set": bool(settings.BOT_TOKEN)
        }

    @app.get("/webhook-debug")
    async def webhook_debug():
        """Просмотр логов webhook для отладки"""
        try:
            with open("/tmp/webhook_debug.log", "r") as f:
                logs = f.read()
            return {"logs": logs}
        except FileNotFoundError:
            return {"logs": "Лог-файл не найден"}