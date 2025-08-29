#!/bin/bash
"""
API Test Script using curl
"""

echo "🚀 Testing SkyPost API endpoints..."

# Test health endpoint
echo -e "\n🔍 Testing health endpoint..."
health_response=$(curl -s http://localhost:8000/health 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ Health endpoint working: $health_response"
else
    echo "❌ Health endpoint failed"
    exit 1
fi

# Test user registration
echo -e "\n🔍 Testing user registration..."
register_response=$(curl -s -X POST http://localhost:8000/auth/register \
    -H "Content-Type: application/json" \
    -d '{
        "email": "test@example.com", 
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User"
    }' 2>/dev/null)

if [ $? -eq 0 ]; then
    echo "✅ Registration response: $register_response"
else
    echo "❌ Registration failed"
fi

# Test user login
echo -e "\n🔍 Testing user login..."
login_response=$(curl -s -X POST http://localhost:8000/auth/login \
    -H "Content-Type: application/json" \
    -d '{
        "email": "test@example.com",
        "password": "testpassword123"
    }' 2>/dev/null)

if [ $? -eq 0 ]; then
    echo "✅ Login response: $login_response"
else
    echo "❌ Login failed"
fi

echo -e "\n✨ Tests completed!"
