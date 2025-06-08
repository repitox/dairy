from apscheduler.schedulers.background import BackgroundScheduler
import pytz
import requests
from db import get_today_tasks, get_today_events, get_recent_purchases, get_conn
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def send_daily_summary():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM users")
            users = cur.fetchall()

    for (user_id,) in users:
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
    requests.post(API_URL, data={"chat_id": user_id, "text": text, "parse_mode": "HTML"})

# Запуск планировщика
def start_scheduler():
    scheduler = BackgroundScheduler(timezone=pytz.timezone("Europe/Moscow"))
    scheduler.add_job(send_daily_summary, "cron", hour=23, minute=26)
    scheduler.start()