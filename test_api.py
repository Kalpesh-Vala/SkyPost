#!/usr/bin/env python3
"""
Quick API test script
"""

import asyncio
import aiohttp
import json


async def test_endpoints():
    """Test the main API endpoints."""
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        # Test health endpoint
        print("🔍 Testing health endpoint...")
        try:
            async with session.get(f"{base_url}/health") as response:
                data = await response.json()
                print(f"✅ Health: {data}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return
        
        # Test user registration
        print("\n🔍 Testing user registration...")
        register_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User"
        }
        
        try:
            async with session.post(f"{base_url}/auth/register", 
                                  json=register_data) as response:
                data = await response.json()
                print(f"✅ Registration: {data}")
        except Exception as e:
            print(f"❌ Registration failed: {e}")
        
        # Test login
        print("\n🔍 Testing user login...")
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        try:
            async with session.post(f"{base_url}/auth/login", 
                                  json=login_data) as response:
                data = await response.json()
                print(f"✅ Login: {data}")
                
                # Extract token for further tests
                if response.status == 200 and 'data' in data and 'token' in data['data']:
                    token = data['data']['token']
                    
                    # Test protected endpoint
                    print("\n🔍 Testing protected endpoint...")
                    headers = {"Authorization": f"Bearer {token}"}
                    
                    async with session.get(f"{base_url}/auth/profile", 
                                         headers=headers) as response:
                        profile_data = await response.json()
                        print(f"✅ Profile: {profile_data}")
                    
        except Exception as e:
            print(f"❌ Login failed: {e}")


if __name__ == "__main__":
    print("🚀 Starting API tests...\n")
    asyncio.run(test_endpoints())
    print("\n✨ Tests completed!")
