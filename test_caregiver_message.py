#!/usr/bin/env python3
"""
Test script to try different methods of sending specific messages to caregiver calls
"""

from vapi import Vapi

def test_caregiver_call_with_message():
    print("🧪 Testing Caregiver Call with Specific Message...")
    
    try:
        vapi = Vapi(token="c6a47844-af14-491c-bf2e-6b344b4f5f26")
        
        # Method 1: Try creating call with specific message
        print("📞 Method 1: Creating call with message parameter...")
        try:
            call = vapi.calls.create(
                phone_number_id="d2d72b53-aeda-48e0-9b1d-1b3c4f51fe67",
                customer={"number": "+17787231783"},
                assistant_id="db1acb44-36f0-42b5-b0c2-6d304aeec781",
                message="Hey! It's Bobby. Your ward hasn't taken their meds today. Maybe check in?"
            )
            print(f"✅ Method 1 successful: {call.id}")
            return True
        except Exception as e:
            print(f"❌ Method 1 failed: {e}")
        
        # Method 2: Try updating call after creation
        print("📞 Method 2: Creating call then updating with message...")
        try:
            call = vapi.calls.create(
                phone_number_id="d2d72b53-aeda-48e0-9b1d-1b3c4f51fe67",
                customer={"number": "+17787231783"},
                assistant_id="db1acb44-36f0-42b5-b0c2-6d304aeec781"
            )
            print(f"✅ Call created: {call.id}")
            
            # Try to update with message
            updated_call = vapi.calls.update(
                call_id=call.id,
                message="Hey! It's Bobby. Your ward hasn't taken their meds today. Maybe check in?"
            )
            print(f"✅ Method 2 successful: {updated_call.id}")
            return True
        except Exception as e:
            print(f"❌ Method 2 failed: {e}")
        
        # Method 3: Just create the call (fallback)
        print("📞 Method 3: Creating basic call...")
        try:
            call = vapi.calls.create(
                phone_number_id="d2d72b53-aeda-48e0-9b1d-1b3c4f51fe67",
                customer={"number": "+17787231783"},
                assistant_id="db1acb44-36f0-42b5-b0c2-6d304aeec781"
            )
            print(f"✅ Method 3 successful: {call.id}")
            print("⚠️  Will use default assistant message")
            return True
        except Exception as e:
            print(f"❌ Method 3 failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ All methods failed: {e}")
        return False

if __name__ == "__main__":
    print("🏥 Caregiver Message Test")
    print("=" * 40)
    test_caregiver_call_with_message()
