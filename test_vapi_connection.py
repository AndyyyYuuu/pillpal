#!/usr/bin/env python3
"""
Quick test to verify VAPI connection with the correct phone number ID
"""

from vapi import Vapi

def test_vapi_connection():
    print("🧪 Testing VAPI Connection with correct Phone Number ID...")
    
    try:
        # Initialize VAPI with your token
        vapi = Vapi(token="c6a47844-af14-491c-bf2e-6b344b4f5f26")
        
        print("✅ VAPI client initialized successfully!")
        
        # Test creating a call
        print("📞 Testing call creation...")
        
        call = vapi.calls.create(
            phone_number_id="d2d72b53-aeda-48e0-9b1d-1b3c4f51fe67",
            customer={"number": "+16472685407"},
            assistant_id="db1acb44-36f0-42b5-b0c2-6d304aeec781"
        )
        
        print(f"✅ Call created successfully: {call.id}")
        print("🎉 VAPI is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ VAPI test failed: {e}")
        return False

if __name__ == "__main__":
    print("🏥 VAPI Connection Test")
    print("=" * 30)
    
    success = test_vapi_connection()
    
    if success:
        print("\n🎉 All systems ready! You can now run the medication reminder system.")
    else:
        print("\n⚠️  There's still an issue with the VAPI configuration.")
