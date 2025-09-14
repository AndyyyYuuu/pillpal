import os
import time
import json
import threading
import pyttsx3
from datetime import datetime, timedelta
from telegram import Bot
from vapi import Vapi

# Import configuration
try:
    from config import *
except ImportError:
    print("❌ Error: config.py not found. Please create it using the provided template.")
    exit(1)

# -------------------------
# CONFIGURATION VALIDATION
# -------------------------
def validate_config():
    """Validate that all required configuration is present"""
    required_vars = [
        'PILL_SCHEDULE', 'BOT_TOKEN', 'CAREGIVER_CHAT_ID', 'VAPI_TOKEN',
        'ASSISTANT_ID', 'PHONE_NUMBER_ID', 'PATIENT_PHONE', 'CAREGIVER_PHONE'
    ]
    
    missing_vars = []
    for var in required_vars:
        if var not in globals() or globals()[var] is None:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing configuration variables: {', '.join(missing_vars)}")
        print("Please update config.py with your actual values.")
        return False
    
    # Check for placeholder values
    if "+1234567890" in str(PATIENT_PHONE) or "+1234567890" in str(CAREGIVER_PHONE):
        print("⚠️  Warning: Please update PATIENT_PHONE and CAREGIVER_PHONE in config.py with actual phone numbers")
        print("   Current values are placeholder numbers. Update them before running the system.")
        return False
    
    return True

# -------------------------
# INITIALIZATION
# -------------------------
# Validate configuration before proceeding
if not validate_config():
    exit(1)

# Initialize services
bot = Bot(token=BOT_TOKEN)
vapi = Vapi(token=VAPI_TOKEN)

# Initialize text-to-speech engine for local announcements
try:
    tts_engine = pyttsx3.init()
    tts_engine.setProperty('rate', TTS_RATE)
    tts_engine.setProperty('volume', TTS_VOLUME)
    print("✅ Text-to-speech engine initialized")
except Exception as e:
    print(f"⚠️  Warning: Could not initialize TTS engine: {e}")
    tts_engine = None

# -------------------------
# LOGGING SYSTEM
# -------------------------
def load_logs():
    """Load medication logs from file"""
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Backup corrupted file
        os.rename(LOG_FILE, LOG_FILE + ".bak")
        return []

def save_logs(logs):
    """Save medication logs to file"""
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

def log_medication_event(time_str, pill_name, status, details=""):
    """Log a medication event"""
    logs = load_logs()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().date().isoformat(),
        "time_str": time_str,
        "pill_name": pill_name,
        "status": status,  # "announced", "telegram_sent", "escalated", "taken"
        "details": details
    }
    logs.append(entry)
    save_logs(logs)
    print(f"📝 Logged: {pill_name} at {time_str} -> {status}")
    return entry

def already_processed_today(time_str):
    """Check if medication was already processed today"""
    logs = load_logs()
    today = datetime.now().date().isoformat()
    for entry in logs:
        if (entry.get("date") == today and 
            entry.get("time_str") == time_str and 
            entry.get("status") in ["announced", "telegram_sent", "escalated"]):
            return True
    return False

# -------------------------
# VOICE ANNOUNCEMENT SYSTEM
# -------------------------
def announce_medication_locally(pill_name):
    """Use VAPI to announce medication through laptop speakers"""
    try:
        message = f"Hello! It's time to take your {pill_name}. Please take it now with water."
        
        # Use local TTS for immediate announcement
        if tts_engine:
            print(f"🔊 Announcing locally: {message}")
            tts_engine.say(message)
            tts_engine.runAndWait()
        
        # Also use VAPI for voice announcement (this will call the patient)
        print(f"📞 Creating VAPI call for medication reminder...")
        call = vapi.calls.create(
            phone_number_id=PHONE_NUMBER_ID,
            customer={"number": PATIENT_PHONE},
            assistant_id=ASSISTANT_ID
        )
        print(f"✅ VAPI call created: {call.id}")
        
        return True
    except Exception as e:
        print(f"❌ Error in voice announcement: {e}")
        return False

# -------------------------
# TELEGRAM NOTIFICATION SYSTEM
# -------------------------
def send_telegram_notification(pill_name, time_str):
    """Send Telegram message to caregiver after delay"""
    try:
        message = f"⏰ Medication Reminder\n\nPatient was reminded to take {pill_name} at {time_str}.\n\nPlease check if they took it."
        bot.send_message(chat_id=config.CAREGIVER_CHAT_ID, text=message)
        print(f"📱 Telegram notification sent to caregiver")
        return True
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")
        return False

# -------------------------
# ESCALATION SYSTEM
# -------------------------
def escalate_to_caregiver(pill_name, time_str):
    """Call caregiver if patient hasn't taken medication"""
    try:
        # Send urgent Telegram message
        urgent_message = f"🚨 URGENT: Patient missed {pill_name} scheduled at {time_str}!\n\nPlease check on them immediately."
        bot.send_message(chat_id=CAREGIVER_CHAT_ID, text=urgent_message)
        
        # Make VAPI call to caregiver
        print(f"📞 Escalating to caregiver via phone call...")
        call = vapi.calls.create(
            phone_number_id=PHONE_NUMBER_ID,
            customer={"number": CAREGIVER_PHONE},
            assistant_id=ASSISTANT_ID
        )
        print(f"✅ Escalation call created: {call.id}")
        
        return True
    except Exception as e:
        print(f"❌ Error in escalation: {e}")
        return False

# -------------------------
# REMINDER MANAGEMENT
# -------------------------
pending_reminders = {}  # time_str -> datetime of reminder

def process_medication_reminder(time_str, pill_name):
    """Process a medication reminder with all steps"""
    print(f"\n{'='*50}")
    print(f"⏰ MEDICATION REMINDER: {pill_name} at {time_str}")
    print(f"{'='*50}")
    
    # Step 1: Voice announcement through VAPI
    if announce_medication_locally(pill_name):
        log_medication_event(time_str, pill_name, "announced", "Voice announcement sent")
        pending_reminders[time_str] = datetime.now()
        
        # Step 2: Send Telegram notification after delay
        def delayed_telegram():
            time.sleep(TELEGRAM_DELAY_SECONDS)
            if send_telegram_notification(pill_name, time_str):
                log_medication_event(time_str, pill_name, "telegram_sent", "Telegram notification sent")
        
        # Run Telegram notification in separate thread
        telegram_thread = threading.Thread(target=delayed_telegram)
        telegram_thread.daemon = True
        telegram_thread.start()
        
        print(f"⏳ Telegram notification will be sent in {TELEGRAM_DELAY_SECONDS} seconds")
    else:
        print(f"❌ Failed to process reminder for {pill_name}")

def check_escalations():
    """Check if any pending reminders need escalation"""
    now = datetime.now()
    to_escalate = []
    
    for time_str, reminder_time in pending_reminders.items():
        elapsed_minutes = (now - reminder_time).total_seconds() / 60
        if elapsed_minutes >= ESCALATION_MINUTES:
            to_escalate.append(time_str)
    
    for time_str in to_escalate:
        pill_name = PILL_SCHEDULE[time_str]
        print(f"\n🚨 ESCALATION: {pill_name} not taken after {ESCALATION_MINUTES} minutes!")
        
        if escalate_to_caregiver(pill_name, time_str):
            log_medication_event(time_str, pill_name, "escalated", 
                               f"Escalated to caregiver after {ESCALATION_MINUTES} minutes")
        
        # Remove from pending reminders
        del pending_reminders[time_str]

# -------------------------
# MAIN SYSTEM LOOP
# -------------------------
def main_loop():
    """Main system loop"""
    print("🏥 Medication Reminder System Started")
    print("=" * 50)
    print(f"📅 Schedule: {PILL_SCHEDULE}")
    print(f"⏱️  Check interval: {CHECK_INTERVAL_SECONDS} seconds")
    print(f"📱 Telegram delay: {TELEGRAM_DELAY_SECONDS} seconds")
    print(f"🚨 Escalation time: {ESCALATION_MINUTES} minutes")
    print("=" * 50)
    print("Press Ctrl+C to exit")
    print()
    
    try:
        while True:
            current_time = datetime.now().strftime("%H:%M")
            
            # Check if it's time for any medication
            if current_time in PILL_SCHEDULE and not already_processed_today(current_time):
                pill_name = PILL_SCHEDULE[current_time]
                process_medication_reminder(current_time, pill_name)
            
            # Check for escalations
            check_escalations()
            
            # Wait before next check
            time.sleep(CHECK_INTERVAL_SECONDS)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down medication reminder system...")
        print("👋 Goodbye!")

# -------------------------
# UTILITY FUNCTIONS
# -------------------------
def show_schedule():
    """Display current medication schedule"""
    print("\n📅 Current Medication Schedule:")
    print("-" * 30)
    for time_str, pill_name in PILL_SCHEDULE.items():
        print(f"  {time_str} - {pill_name}")
    print()

def show_recent_logs(limit=10):
    """Show recent medication logs"""
    logs = load_logs()
    recent_logs = logs[-limit:] if logs else []
    
    print(f"\n📋 Recent Medication Logs (last {len(recent_logs)} entries):")
    print("-" * 50)
    for log in recent_logs:
        timestamp = log.get('timestamp', 'Unknown')
        time_str = log.get('time_str', 'Unknown')
        pill_name = log.get('pill_name', 'Unknown')
        status = log.get('status', 'Unknown')
        print(f"  {timestamp[:19]} | {time_str} | {pill_name} | {status}")
    print()

if __name__ == "__main__":
    # Show initial information
    show_schedule()
    show_recent_logs()
    
    # Start the main system
    main_loop()
