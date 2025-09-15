#!/usr/bin/env python3
"""
Test validation for profile update API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_validation():
    """Test the profile update validation."""
    
    # Login to get token
    login_data = {
        "email": "testuser123@example.com", 
        "password": "testpassword123"
    }
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    token = login_response.json().get('data', {}).get('token')
    
    if not token:
        print("❌ Could not get token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Invalid short name
    print("🧪 Test 1: Invalid short name")
    update_data = {"first_name": "A"}  # Too short
    response = requests.put(f"{BASE_URL}/auth/profile", json=update_data, headers=headers)
    print(f"Status: {response.status_code}, Response: {response.json()}")
    
    # Test 2: Bio too long
    print("\n🧪 Test 2: Bio too long")
    update_data = {"bio": "x" * 600}  # Too long
    response = requests.put(f"{BASE_URL}/auth/profile", json=update_data, headers=headers)
    print(f"Status: {response.status_code}, Response: {response.json()}")
    
    # Test 3: Valid update
    print("\n🧪 Test 3: Valid update")
    update_data = {"first_name": "Valid", "bio": "Short bio"}
    response = requests.put(f"{BASE_URL}/auth/profile", json=update_data, headers=headers)
    print(f"Status: {response.status_code}, Response: {response.json()}")

if __name__ == "__main__":
    test_validation()
