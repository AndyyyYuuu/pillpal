import os
import time
import json
from datetime import datetime, timedelta
from telegram import Bot
from vapi import Vapi

# -------------------------
# CONFIG
# -------------------------
pill_schedule = {
    "17:37": "Vitamin C",
    "18:00": "Multivitamin" 
}

LOG_FILE = "adherence_log.json"
CHECK_INTERVAL_SECONDS = 5  # testing interval
ESCALATION_MINUTES = 0.5    # 30 seconds for escalation
TELEGRAM_DELAY_SECONDS = 10  # Wait 10 seconds before calling patient

# Telegram setup (caregiver only)
BOT_TOKEN = "8344896751:AAE8__3bTY4wEs5mzvItr9-Rm5cGdkrJhQk"
CAREGIVER_CHAT_ID = 8044496961   # caregiver chat_id
bot = Bot(token=BOT_TOKEN)

# VAPI setup
vapi = Vapi(token="c6a47844-af14-491c-bf2e-6b344b4f5f26")
ASSISTANT_ID = "db1acb44-36f0-42b5-b0c2-6d304aeec781"  # For patient calls
CAREGIVER_ASSISTANT_ID = "29125bb2-c574-42e5-a493-68922f8cdd88"  # For caregiver calls
PHONE_NUMBER_ID = "d2d72b53-aeda-48e0-9b1d-1b3c4f51fe67"

# -------------------------
# LOGGING HELPERS
# -------------------------
def load_logs():
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        os.rename(LOG_FILE, LOG_FILE + ".bak")
        return []

def save_logs(logs):
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

def log_entry(time_str, pill_name, status):
    logs = load_logs()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().date().isoformat(),
        "time_str": time_str,
        "pill_name": pill_name,
        "status": status
    }
    logs.append(entry)
    save_logs(logs)
    return entry

def already_logged_today(time_str):
    logs = load_logs()
    today = datetime.now().date().isoformat()
    for e in logs:
        if e.get("date") == today and e.get("time_str") == time_str:
            return True
    return False

# -------------------------
# TELEGRAM HELPERS (caregiver)
# -------------------------
def send_caregiver_message(text):
    try:
        bot.send_message(chat_id=CAREGIVER_CHAT_ID, text=text)
        print(f"✅ Telegram message sent: {text}")
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")

# -------------------------
# TELEGRAM MESSAGE TO PATIENT
# -------------------------
def send_patient_message(pill_name, time_str):
    """Send Telegram message to patient about medication"""
    try:
        message = f"⏰ Medication Reminder\n\nIt's time to take your {pill_name} at {time_str}.\n\nPlease take it now with water."
        bot.send_message(chat_id=CAREGIVER_CHAT_ID, text=message)  # Using caregiver chat for now
        print(f"✅ Patient message sent: {message}")
        return True
    except Exception as e:
        print(f"❌ Failed to send patient message: {e}")
        return False

# -------------------------
# VAPI CALL TO PATIENT
# -------------------------
def call_patient_reminder(pill_name):
    """Call patient to remind them of medication"""
    message = f"Hello! It's time to take your {pill_name}. Please take it now with water."
    print(f"📞 Calling patient: {message}")
    
    try:
        call = vapi.calls.create(
            phone_number_id=PHONE_NUMBER_ID,
            customer={"number": "+16472685407"},
            assistant_id=ASSISTANT_ID
        )
        print(f"✅ VAPI call created for patient: {call.id}")
        return True
    except Exception as e:
        print(f"❌ VAPI call failed: {e}")
        return False

# -------------------------
# REMINDER / ESCALATION
# -------------------------
pending_reminders = {}  # time_str -> datetime of reminder

def remind_patient(time_str, pill_name):
    print(f"\n*** Reminder: It's {time_str}! Take your {pill_name} ***")
    
    # Step 1: Send message to patient
    if send_patient_message(pill_name, time_str):
        log_entry(time_str, pill_name, "message_sent")
        
        # Step 2: Wait 10 seconds, then call patient
        def delayed_patient_call():
            time.sleep(TELEGRAM_DELAY_SECONDS)
            if call_patient_reminder(pill_name):
                log_entry(time_str, pill_name, "patient_called")
            else:
                log_entry(time_str, pill_name, "patient_call_failed")
        
        # Run patient call in separate thread
        import threading
        call_thread = threading.Thread(target=delayed_patient_call)
        call_thread.daemon = True
        call_thread.start()
        
        print(f"⏳ Patient call will be made in {TELEGRAM_DELAY_SECONDS} seconds")
        pending_reminders[time_str] = datetime.now()
    else:
        print(f"❌ Failed to send patient message for {pill_name}")

def check_escalations():
    now = datetime.now()
    to_escalate = []
    for time_str, reminder_time in pending_reminders.items():
        if (now - reminder_time).total_seconds() > ESCALATION_MINUTES * 60:
            to_escalate.append(time_str)
    for time_str in to_escalate:
        pill_name = pill_schedule[time_str]
        print(f"*** ESCALATION: {pill_name} not taken! Sending alerts to caregiver ***")
        
        # Send message to caregiver
        caregiver_message = f"🚨 URGENT: Patient missed {pill_name} scheduled at {time_str}!\n\nPlease check on them immediately."
        send_caregiver_message(caregiver_message)
        
        # Call caregiver with specific message
        try:
            print("📞 Calling caregiver...")
            call = vapi.calls.create(
                phone_number_id=PHONE_NUMBER_ID,
                customer={"number": "+17787231783"},  # Caregiver phone number
                assistant_id=CAREGIVER_ASSISTANT_ID
            )
            print(f"✅ VAPI call created for caregiver: {call.id}")
            print("🎯 Caregiver will hear Bobby's message about their ward not taking medication")
                
        except Exception as e:
            print(f"❌ VAPI call to caregiver failed: {e}")
        
        log_entry(time_str, pill_name, "missed/escalated")
        del pending_reminders[time_str]

# -------------------------
# MAIN LOOP
# -------------------------
def main_loop():
    print("Pill reminder system started. Press Ctrl+C to exit.")
    print("✅ Workflow: Message → Wait 10s → Call Patient → Escalate to Caregiver if needed")
    print(f"⏰ Next medication: {list(pill_schedule.keys())[0]} - {list(pill_schedule.values())[0]}")
    try:
        while True:
            now = datetime.now().strftime("%H:%M")
            # schedule patient reminders
            if now in pill_schedule and not already_logged_today(now):
                remind_patient(now, pill_schedule[now])
            # check for caregiver escalation
            check_escalations()
            time.sleep(CHECK_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nShutting down. Bye.")

if __name__ == "__main__":
    main_loop()
