#!/usr/bin/env python3
"""
Test script for profile update API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_profile_update():
    """Test the profile update functionality."""
    
    # First, register a test user
    print("🔧 Testing Profile Update API...")
    
    # Register user
    register_data = {
        "email": "testuser123@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    print("📝 Registering test user...")
    register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print(f"Register response: {register_response.status_code}")
    print(f"Register data: {register_response.json()}")
    
    if register_response.status_code != 201:
        # Try to login instead (user might already exist)
        print("🔐 User might exist, trying to login...")
        login_data = {
            "email": "testuser123@example.com", 
            "password": "testpassword123"
        }
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Login response: {login_response.status_code}")
        login_json = login_response.json()
        print(f"Login data: {login_json}")
        
        if login_response.status_code != 200:
            print("❌ Failed to login")
            return
            
        token = login_json.get('data', {}).get('token')
    else:
        token = register_response.json().get('data', {}).get('token')
    
    if not token:
        print("❌ No token received")
        return
    
    print(f"✅ Got token: {token[:20]}...")
    
    # Test profile update
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "first_name": "Updated",
        "last_name": "Name", 
        "bio": "This is my updated bio"
    }
    
    print("🔄 Testing profile update...")
    print(f"Update data: {update_data}")
    
    update_response = requests.put(
        f"{BASE_URL}/auth/profile", 
        json=update_data,
        headers=headers
    )
    
    print(f"Update response status: {update_response.status_code}")
    print(f"Update response: {update_response.json()}")
    
    if update_response.status_code == 200:
        print("✅ Profile update successful!")
    else:
        print("❌ Profile update failed!")
        
    # Get profile to verify
    print("📄 Getting updated profile...")
    profile_response = requests.get(f"{BASE_URL}/auth/profile", headers=headers)
    print(f"Profile response: {profile_response.status_code}")
    print(f"Profile data: {profile_response.json()}")

if __name__ == "__main__":
    test_profile_update()
