"""
Configuration file for Medication Reminder System
Update these values according to your setup
"""

# -------------------------
# MEDICATION SCHEDULE
# -------------------------
# Add your medication times here (24-hour format)
PILL_SCHEDULE = {
    "12:00": "Vitamin C",
    "14:00": "Multivitamin",
    # Add more medications as needed
    # "18:00": "Evening Medication",
    # "22:00": "Night Medication"
}

# -------------------------
# TELEGRAM BOT CONFIGURATION
# -------------------------
# Your Telegram Bot Token (from BotFather)
BOT_TOKEN = "8344896751:AAE8__3bTY4wEs5mzvItr9-Rm5cGdkrJhQk"

# Caregiver's Telegram Chat ID (where notifications will be sent)
CAREGIVER_CHAT_ID = 8044496961

# -------------------------
# VAPI CONFIGURATION
# -------------------------
# Your VAPI API Token
VAPI_TOKEN = "c6a47844-af14-491c-bf2e-6b344b4f5f26"

# VAPI Assistant IDs for voice calls
ASSISTANT_ID = "db1acb44-36f0-42b5-b0c2-6d304aeec781"  # For patient calls
CAREGIVER_ASSISTANT_ID = "29125bb2-c574-42e5-a493-68922f8cdd88"  # For caregiver calls

# VAPI Phone Number ID (this should be a UUID from your VAPI dashboard)
PHONE_NUMBER_ID = "d2d72b53-aeda-48e0-9b1d-1b3c4f51fe67"

# -------------------------
# PHONE NUMBERS
# -------------------------
# Patient's phone number (who will receive medication reminders)
PATIENT_PHONE = "+16472685407"  # Patient's phone number

# Caregiver's phone number (who will be called if medication is missed)
CAREGIVER_PHONE = "+17787231783"  # Caregiver's phone number

# -------------------------
# TIMING CONFIGURATION
# -------------------------
# How often to check for medication times (in seconds)
CHECK_INTERVAL_SECONDS = 5

# Delay before sending Telegram notification (in seconds)
TELEGRAM_DELAY_SECONDS = 5

# Minutes to wait before escalating to phone call if medication not taken
ESCALATION_MINUTES = 30

# -------------------------
# LOGGING CONFIGURATION
# -------------------------
# File to store medication logs
LOG_FILE = "medication_log.json"

# -------------------------
# TEXT-TO-SPEECH CONFIGURATION
# -------------------------
# Speech rate (words per minute)
TTS_RATE = 150

# Speech volume (0.0 to 1.0)
TTS_VOLUME = 0.8
