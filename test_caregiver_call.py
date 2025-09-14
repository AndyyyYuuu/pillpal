#!/usr/bin/env python3
"""
Quick test to directly call the caregiver
"""

from vapi import Vapi
from telegram import Bot

# Configuration
BOT_TOKEN = "8344896751:AAE8__3bTY4wEs5mzvItr9-Rm5cGdkrJhQk"
CAREGIVER_CHAT_ID = 8044496961
VAPI_TOKEN = "c6a47844-af14-491c-bf2e-6b344b4f5f26"
ASSISTANT_ID = "db1acb44-36f0-42b5-b0c2-6d304aeec781"  # For patient calls
CAREGIVER_ASSISTANT_ID = "29125bb2-c574-42e5-a493-68922f8cdd88"  # For caregiver calls
PHONE_NUMBER_ID = "d2d72b53-aeda-48e0-9b1d-1b3c4f51fe67"
CAREGIVER_PHONE = "+17787231783"  # Caregiver phone number

def test_caregiver_call():
    print("🧪 Testing Caregiver Call...")
    
    try:
        # Initialize services
        bot = Bot(token=BOT_TOKEN)
        vapi = Vapi(token=VAPI_TOKEN)
        
        # Send Telegram message
        message = "🧪 TEST: This is a test message for caregiver call functionality"
        bot.send_message(chat_id=CAREGIVER_CHAT_ID, text=message)
        print("✅ Telegram test message sent")
        
        # Make VAPI call to caregiver
        print("📞 Making test call to caregiver...")
        call = vapi.calls.create(
            phone_number_id=PHONE_NUMBER_ID,
            customer={"number": CAREGIVER_PHONE},
            assistant_id=CAREGIVER_ASSISTANT_ID
        )
        print(f"✅ Caregiver call created: {call.id}")
        print("🎉 Test completed! Check your phone for the call.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("🏥 Caregiver Call Test")
    print("=" * 30)
    test_caregiver_call()
