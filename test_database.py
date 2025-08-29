#!/usr/bin/env python3
"""
Database connection test script
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_database_connection():
    """Test database connection step by step."""
    print("🔍 Testing database connection...")
    
    # Test 1: Check if asyncpg is installed
    try:
        import asyncpg
        print("✅ asyncpg module available")
    except ImportError as e:
        print(f"❌ asyncpg not installed: {e}")
        print("💡 Run: pip install asyncpg")
        return False
    
    # Test 2: Check if gino is working
    try:
        from gino import Gino
        print("✅ Gino module available")
    except ImportError as e:
        print(f"❌ Gino not available: {e}")
        return False
    
    # Test 3: Check config loading
    try:
        from config.settings import config
        print(f"✅ Configuration loaded: {config.DATABASE_URL}")
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False
    
    # Test 4: Try direct asyncpg connection
    try:
        conn = await asyncpg.connect(config.DATABASE_URL)
        await conn.close()
        print("✅ Direct asyncpg connection successful")
    except Exception as e:
        print(f"❌ Direct asyncpg connection failed: {e}")
        print("\n🔍 Possible issues:")
        print("1. PostgreSQL not running: sudo systemctl start postgresql")
        print("2. Database doesn't exist: createdb skypost_db")
        print("3. Wrong credentials in .env file")
        print("4. PostgreSQL not installed: sudo apt install postgresql")
        return False
    
    # Test 5: Try Gino connection
    try:
        from app.utils.database import init_db, close_db
        await init_db()
        await close_db()
        print("✅ Gino connection successful")
    except Exception as e:
        print(f"❌ Gino connection failed: {e}")
        return False
    
    print("\n🎉 All database tests passed!")
    return True

def main():
    """Main test function."""
    result = asyncio.run(test_database_connection())
    sys.exit(0 if result else 1)

if __name__ == "__main__":
    main()
