#!/usr/bin/env python3
"""
Script to help find your VAPI Phone Number ID
This will list your available phone numbers from VAPI
"""

from vapi import Vapi

def find_phone_numbers():
    print("🔍 Finding your VAPI Phone Numbers...")
    
    try:
        # Initialize VAPI with your token
        vapi = Vapi(token="c6a47844-af14-491c-bf2e-6b344b4f5f26")
        
        print("✅ Connected to VAPI successfully!")
        
        # Get phone numbers
        print("\n📞 Available Phone Numbers:")
        print("-" * 50)
        
        # Try to get phone numbers (this might vary based on VAPI API)
        try:
            # This is a common way to list phone numbers in VAPI
            phone_numbers = vapi.phone_numbers.list()
            
            for phone in phone_numbers.data:
                print(f"Phone Number: {phone.number}")
                print(f"Phone Number ID: {phone.id}")
                print(f"Status: {phone.status}")
                print("-" * 30)
                
        except AttributeError:
            print("⚠️  Could not list phone numbers directly.")
            print("Please check your VAPI dashboard for the Phone Number ID.")
            print("It should look like: '12345678-1234-1234-1234-123456789012'")
            
    except Exception as e:
        print(f"❌ Error connecting to VAPI: {e}")
        print("\nTroubleshooting:")
        print("1. Check your VAPI token is correct")
        print("2. Make sure you have phone numbers set up in your VAPI dashboard")
        print("3. The Phone Number ID should be a UUID, not the actual phone number")

if __name__ == "__main__":
    print("🏥 VAPI Phone Number ID Finder")
    print("=" * 40)
    find_phone_numbers()
