#!/usr/bin/env python3
"""
Test which phone numbers are verified in your VAPI account
"""

from vapi import Vapi

def test_phone_number(phone_number, description):
    print(f"🧪 Testing {description}: {phone_number}")
    
    try:
        vapi = Vapi(token="c6a47844-af14-491c-bf2e-6b344b4f5f26")
        
        call = vapi.calls.create(
            phone_number_id="d2d72b53-aeda-48e0-9b1d-1b3c4f51fe67",
            customer={"number": phone_number},
            assistant_id="db1acb44-36f0-42b5-b0c2-6d304aeec781"
        )
        
        print(f"✅ {description} call successful: {call.id}")
        return True
        
    except Exception as e:
        print(f"❌ {description} call failed: {e}")
        return False

if __name__ == "__main__":
    print("🏥 Phone Number Verification Test")
    print("=" * 40)
    
    # Test patient number (should work)
    patient_works = test_phone_number("+16472685407", "Patient")
    print()
    
    # Test caregiver number (might not work)
    caregiver_works = test_phone_number("+14374312360", "Caregiver")
    print()
    
    if patient_works and caregiver_works:
        print("🎉 Both numbers are verified and working!")
    elif patient_works:
        print("⚠️  Only patient number is verified. You need to verify the caregiver number in VAPI dashboard.")
    else:
        print("❌ Neither number is verified. Check your VAPI account settings.")
