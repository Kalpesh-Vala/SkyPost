#!/usr/bin/env python3
"""
Alternative database setup using direct Gino connection
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gino import Gino
from config.settings import config

async def test_gino_direct():
    """Test Gino with direct connection string."""
    print("🔧 Testing Gino with direct connection...")
    
    db = Gino()
    
    try:
        # Try different connection string formats
        connection_strings = [
            f"postgresql+asyncpg://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}",
            config.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
            config.DATABASE_URL
        ]
        
        for i, conn_str in enumerate(connection_strings, 1):
            print(f"\n🔍 Trying connection format {i}: {conn_str[:50]}...")
            try:
                await db.set_bind(conn_str)
                print(f"✅ Connection {i} successful!")
                
                # Test table creation
                from app.models.user import User
                await db.gino.create_all()
                print("✅ Tables created successfully!")
                
                await db.pop_bind().close()
                return True
                
            except Exception as e:
                print(f"❌ Connection {i} failed: {str(e)}")
                try:
                    if db.bind:
                        await db.pop_bind().close()
                except:
                    pass
    
    except Exception as e:
        print(f"❌ General error: {str(e)}")
    
    return False

def main():
    """Main test function."""
    result = asyncio.run(test_gino_direct())
    print(f"\n{'✅ SUCCESS' if result else '❌ FAILED'}")
    sys.exit(0 if result else 1)

if __name__ == "__main__":
    main()
