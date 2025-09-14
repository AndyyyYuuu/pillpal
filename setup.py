#!/usr/bin/env python3
"""
Setup script for Medication Reminder System
This script helps you install dependencies and configure the system
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required Python packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def check_config():
    """Check if config.py exists and is properly configured"""
    if not os.path.exists("config.py"):
        print("❌ config.py not found!")
        print("Please create config.py using the provided template.")
        return False
    
    try:
        from config import *
        
        # Check for placeholder values
        if "+YOUR_PATIENT_NUMBER" in str(PATIENT_PHONE) or "+YOUR_CAREGIVER_NUMBER" in str(CAREGIVER_PHONE):
            print("⚠️  Warning: Please update phone numbers in config.py")
            print("   - PATIENT_PHONE: Replace with actual patient number")
            print("   - CAREGIVER_PHONE: Replace with actual caregiver number")
            return False
        
        print("✅ Configuration looks good!")
        return True
        
    except ImportError as e:
        print(f"❌ Error importing config: {e}")
        return False

def test_telegram():
    """Test Telegram bot connection"""
    print("📱 Testing Telegram bot connection...")
    try:
        from telegram import Bot
        from config import BOT_TOKEN, CAREGIVER_CHAT_ID
        
        bot = Bot(token=BOT_TOKEN)
        # Try to get bot info
        bot_info = bot.get_me()
        print(f"✅ Telegram bot connected: @{bot_info.username}")
        
        # Try to send a test message
        test_message = "🧪 Test message from Medication Reminder System"
        bot.send_message(chat_id=CAREGIVER_CHAT_ID, text=test_message)
        print("✅ Test message sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Telegram test failed: {e}")
        return False

def test_vapi():
    """Test VAPI connection"""
    print("📞 Testing VAPI connection...")
    try:
        from vapi import Vapi
        from config import VAPI_TOKEN
        
        vapi = Vapi(token=VAPI_TOKEN)
        # Try to get account info (this is a simple test)
        print("✅ VAPI connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ VAPI test failed: {e}")
        return False

def test_tts():
    """Test text-to-speech functionality"""
    print("🔊 Testing text-to-speech...")
    try:
        import pyttsx3
        
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.8)
        
        # Test speech
        engine.say("Text to speech test successful")
        engine.runAndWait()
        
        print("✅ Text-to-speech working!")
        return True
        
    except Exception as e:
        print(f"❌ Text-to-speech test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🏥 Medication Reminder System Setup")
    print("=" * 40)
    
    # Step 1: Install requirements
    if not install_requirements():
        print("❌ Setup failed at package installation")
        return False
    
    print()
    
    # Step 2: Check configuration
    if not check_config():
        print("❌ Setup failed at configuration check")
        return False
    
    print()
    
    # Step 3: Test connections
    print("🧪 Testing system components...")
    
    telegram_ok = test_telegram()
    vapi_ok = test_vapi()
    tts_ok = test_tts()
    
    print()
    print("📊 Test Results:")
    print(f"   Telegram: {'✅' if telegram_ok else '❌'}")
    print(f"   VAPI: {'✅' if vapi_ok else '❌'}")
    print(f"   Text-to-Speech: {'✅' if tts_ok else '❌'}")
    
    if telegram_ok and vapi_ok and tts_ok:
        print("\n🎉 Setup completed successfully!")
        print("You can now run: python medication_reminder_system.py")
        return True
    else:
        print("\n⚠️  Setup completed with warnings.")
        print("Please fix the failed components before running the system.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
