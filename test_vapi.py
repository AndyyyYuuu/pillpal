#!/usr/bin/env python3
"""
Simple test script to verify VAPI connection and configuration
"""

from vapi import Vapi

# Test VAPI connection
def test_vapi_connection():
    print("🧪 Testing VAPI Connection...")
    
    try:
        # Initialize VAPI with your token
        vapi = Vapi(token="c6a47844-af14-491c-bf2e-6b344b4f5f26")
        
        print("✅ VAPI client initialized successfully!")
        
        # Test creating a call (this will fail if phone number is invalid, but that's expected)
        print("📞 Testing call creation...")
        
        call = vapi.calls.create(
            phone_number_id="647-268-5407",
            customer={"number": "+1234567890"},  # This will fail with invalid number, but shows the API works
            assistant_id="db1acb44-36f0-42b5-b0c2-6d304aeec781"
        )
        
        print(f"✅ Call created successfully: {call.id}")
        return True
        
    except Exception as e:
        print(f"❌ VAPI test failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check that your VAPI token is correct")
        print("2. Verify your assistant ID is valid")
        print("3. Make sure your phone number ID is set up correctly")
        print("4. Update the phone number to a real number for testing")
        return False

if __name__ == "__main__":
    print("🏥 VAPI Connection Test")
    print("=" * 30)
    
    success = test_vapi_connection()
    
    if success:
        print("\n🎉 VAPI connection test passed!")
    else:
        print("\n⚠️  VAPI connection test failed. Please check your configuration.")
