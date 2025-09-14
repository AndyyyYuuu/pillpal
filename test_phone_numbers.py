#!/usr/bin/env python3
"""
Test script to verify phone numbers are configured correctly
"""

try:
    from config import PATIENT_PHONE, CAREGIVER_PHONE
    print("📱 Phone Number Configuration Test")
    print("=" * 40)
    print(f"Patient Phone (reminders): {PATIENT_PHONE}")
    print(f"Caregiver Phone (escalation): {CAREGIVER_PHONE}")
    print()
    
    # Verify the numbers are correct
    if PATIENT_PHONE == "+16472685407":
        print("✅ Patient phone number is correct")
    else:
        print(f"❌ Patient phone number should be +16472685407, got {PATIENT_PHONE}")
    
    if CAREGIVER_PHONE == "+14374312360":
        print("✅ Caregiver phone number is correct")
    else:
        print(f"❌ Caregiver phone number should be +14374312360, got {CAREGIVER_PHONE}")
    
    print()
    print("🎯 System will:")
    print(f"   📞 Call {PATIENT_PHONE} for medication reminders")
    print(f"   📞 Call {CAREGIVER_PHONE} if medication is missed")
    
except ImportError as e:
    print(f"❌ Error importing config: {e}")
