#!/usr/bin/env python3
"""
Test modern SQLAlchemy async setup
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_modern_sqlalchemy():
    """Test modern SQLAlchemy async setup."""
    print("🔧 Testing modern SQLAlchemy async setup...")
    
    try:
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, Boolean, Text
        from sqlalchemy.sql import func
        from config.settings import config
        
        print("✅ SQLAlchemy async imports successful")
        
        # Convert postgresql:// to postgresql+asyncpg://
        database_url = config.DATABASE_URL
        if database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://')
        
        print(f"🔗 Connecting to: {database_url[:50]}...")
        
        engine = create_async_engine(database_url, echo=False)
        
        # Test connection
        async with engine.begin() as conn:
            from sqlalchemy import text
            result = await conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
        
        # Test table creation
        metadata = MetaData()
        
        test_table = Table(
            'test_table',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(50)),
            Column('created_at', DateTime, default=func.now())
        )
        
        async with engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
            print("✅ Table creation successful")
        
        # Clean up test table
        async with engine.begin() as conn:
            await conn.run_sync(metadata.drop_all)
            print("✅ Table cleanup successful")
        
        await engine.dispose()
        print("✅ Connection closed")
        
        print("\n🎉 Modern SQLAlchemy setup works perfectly!")
        return True
        
    except Exception as e:
        print(f"❌ Modern SQLAlchemy test failed: {str(e)}")
        return False

def main():
    """Main test function."""
    result = asyncio.run(test_modern_sqlalchemy())
    sys.exit(0 if result else 1)

if __name__ == "__main__":
    main()
