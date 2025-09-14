import time
import json
from datetime import datetime

pill_schedule = {
    "10:00": "Vitamin C",
    "14:00": "Multivitamin"
}

log_file = "adherence_log.json"

try:
    with open(log_file, "r") as f:
        adherence_log = json.load(f)
except FileNotFoundError:
    adherence_log = {}

def remind_user(time_str, pill_name):
    print(f"\nReminder: It's {time_str}! Time to take your {pill_name}.")
    response = input("Did you take it? (yes/no): ").strip().lower()
    status = "taken" if response == "yes" else "missed"
    
    adherence_log[time_str] = status
    with open(log_file, "w") as f:
        json.dump(adherence_log, f, indent=4)
    
    print(f"Logged: {pill_name} at {time_str} -> {status}")

print("Pill reminder system started. Press Ctrl+C to exit.")

while True:
    now = datetime.now().strftime("%H:%M")
    if now in pill_schedule and now not in adherence_log:
        remind_user(now, pill_schedule[now])
    time.sleep(30)
from telegram import Bot

BOT_TOKEN = "8344896751:AAE8__3bTY4wEs5mzvItr9-Rm5cGdkrJhQk"  # paste the token BotFather gave you

bot = Bot(token=BOT_TOKEN)

# this gets info about the most recent message you sent the bot
updates = bot.get_updates()

for u in updates:
    print(u.message.chat.id, u.message.chat.first_name)