#!/usr/bin/env python3
"""
Test Instagram API Credentials
This script helps test if your Instagram API credentials are working.
"""

import os
import requests
from dotenv import load_dotenv

def test_credentials():
    """Test Instagram API credentials"""
    
    # Load environment variables
    load_dotenv()
    
    access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
    business_id = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')
    
    if not access_token:
        print("❌ INSTAGRAM_ACCESS_TOKEN not found in .env file")
        return False
    
    if not business_id:
        print("❌ INSTAGRAM_BUSINESS_ACCOUNT_ID not found in .env file")
        return False
    
    print("🔍 Testing Instagram API credentials...")
    print(f"Business ID: {business_id}")
    print(f"Access Token: {access_token[:20]}...")
    
    # Test Instagram Graph API
    try:
        url = f"https://graph.facebook.com/v19.0/{business_id}"
        params = {
            'access_token': access_token,
            'fields': 'id,name,username'
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Instagram API credentials are working!")
            print(f"Account: {data.get('name', 'Unknown')} (@{data.get('username', 'unknown')})")
            return True
        else:
            print(f"❌ Instagram API error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing credentials: {e}")
        return False

def main():
    print("🧪 Instagram API Credentials Test")
    print("=" * 40)
    print()
    
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please run: python3 setup_env.py")
        return
    
    if test_credentials():
        print()
        print("🎉 Your credentials are working!")
        print("You can now deploy your bot.")
    else:
        print()
        print("❌ Credentials test failed.")
        print("Please check your Instagram API credentials.")

if __name__ == "__main__":
    main() 