"""
Конфигурация приложения
"""
import os
from dotenv import load_dotenv

# Загружаем .env только если переменная DATABASE_URL не установлена
if not os.getenv("DATABASE_URL"):
    load_dotenv()

class Settings:
    """Настройки приложения"""
    
    # Telegram Bot
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    DOMAIN: str = os.getenv("DOMAIN", "https://dialist.ru")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    # Устанавливаем DATABASE_URL для продакшена NetAngels если не задан
    if not DATABASE_URL:
        DATABASE_URL = "postgresql://c107597_dialist_ru:ZoXboBiphobem19@postgres.c107597.h2:5432/c107597_dialist_ru"
        os.environ["DATABASE_URL"] = DATABASE_URL
        print(f"🔧 Установлен DATABASE_URL для NetAngels: {DATABASE_URL[:50]}...")
    
    # Webhook
    @property
    def WEBHOOK_PATH(self) -> str:
        return f"/webhook/{self.BOT_TOKEN}"
    
    @property
    def WEBHOOK_URL(self) -> str:
        return f"{self.DOMAIN}{self.WEBHOOK_PATH}"
    
    # Testing
    TESTING: bool = os.getenv("TESTING", "false").lower() == "true"
    TEST_DATABASE_URL: str = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")
    
    # Security
    VERIFY_TELEGRAM_SIGNATURE: bool = os.getenv("VERIFY_TELEGRAM_SIGNATURE", "false").lower() == "true"

settings = Settings()