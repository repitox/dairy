import subprocess
import time
import os

bot_file = "bot.py"

def run_bot():
    return subprocess.Popen(["python3", bot_file])

def watch_file():
    last_mtime = os.path.getmtime(bot_file)
    process = run_bot()
    
    try:
        while True:
            time.sleep(1)
            new_mtime = os.path.getmtime(bot_file)
            if new_mtime != last_mtime:
                print("Изменение обнаружено. Перезапуск бота...")
                process.terminate()
                process = run_bot()
                last_mtime = new_mtime
    except KeyboardInterrupt:
        print("Остановка...")
        process.terminate()

if __name__ == "__main__":
    watch_file()