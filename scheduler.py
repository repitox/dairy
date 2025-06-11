from apscheduler.schedulers.background import BackgroundScheduler
import pytz
import requests
from db import get_today_tasks, get_today_events, get_recent_purchases, get_conn
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def send_daily_summary():
    print("⏰ Запуск ежедневной рассылки...")
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM users")
            users = cur.fetchall()
            print("💬 Все user_id из БД:", users)
            print(f"🔍 Найдено пользователей: {len(users)}")

    for row in users:
        user_id = row["user_id"]
        print(f"📤 Отправка сводки для пользователя {user_id}...")

        tasks = get_today_tasks(user_id)
        events = get_today_events(user_id)
        shopping = get_recent_purchases(user_id)

        message = format_summary(tasks, events, shopping)
        send_message(user_id, message)

def format_summary(tasks, events, shopping):
    lines = ["📌 <b>Задачи</b>:"]
    lines += [f"- [ ] {t['title']} ({t['due_date']})" for t in tasks] or ["Нет задач"]

    lines += ["", "📅 <b>Встречи</b>:"]
    lines += [f"- {e['title']} — {e['start_at'][11:16]}" for e in events] or ["Нет встреч"]

    lines += ["", "🛒 <b>Покупки</b>:"]
    lines += [f"- {s['title']}" for s in shopping] or ["Нет покупок"]

    return "\n".join(lines)

def send_message(user_id, text):
    print(f"📨 Отправка сообщения Telegram для {user_id}")
    response = requests.post(API_URL, data={"chat_id": user_id, "text": text, "parse_mode": "HTML"})
    print(f"➡️ Статус ответа: {response.status_code}, текст: {response.text}")

# Запуск планировщика
def start_scheduler():
    print("🌀 Планировщик запускается...")
    scheduler = BackgroundScheduler(timezone=pytz.timezone("Europe/Moscow"))
    scheduler.add_job(send_daily_summary, "interval", minutes=1)
    scheduler.start()
    print("✅ Планировщик запущен.")