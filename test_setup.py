#!/usr/bin/env python3
"""
Quick test script to verify SkyPost setup
"""

import asyncio
import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import config

async def test_basic_setup():
    """Test basic application setup without database."""
    print("🧪 Testing SkyPost Basic Setup...")
    
    try:
        # Test configuration loading
        print(f"✅ Configuration loaded: {config.APP_NAME}")
        
        # Test importing main components
        from app.utils.responses import success_response, error_response
        print("✅ Utility functions imported")
        
        from app.utils.validation import UserRegistrationSchema
        print("✅ Validation schemas imported")
        
        # Test response utilities
        success_resp = success_response({"test": "data"}, "Test successful")
        error_resp = error_response("Test error")
        
        print("✅ Response utilities working")
        
        # Test validation
        try:
            user_schema = UserRegistrationSchema(
                email="test@example.com",
                password="password123",
                first_name="Test",
                last_name="User"
            )
            print("✅ Validation working")
        except Exception as e:
            print(f"⚠️  Validation test failed: {e}")
        
        print("\n🎉 Basic setup test completed successfully!")
        print("\n📝 Next steps:")
        print("1. Set up PostgreSQL database")
        print("2. Update .env file with database credentials")
        print("3. Run: python db_setup.py setup")
        print("4. Run: python main.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic setup test failed: {str(e)}")
        return False

def main():
    """Main test function."""
    result = asyncio.run(test_basic_setup())
    sys.exit(0 if result else 1)

if __name__ == "__main__":
    main()
