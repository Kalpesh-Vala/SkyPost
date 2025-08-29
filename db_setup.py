#!/usr/bin/env python3
"""
Database setup and management script
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.database import init_db, create_tables, drop_tables, close_db
from app.models import User, Message, Attachment

async def setup_database():
    """Set up the database with tables."""
    print("🔧 Setting up database...")
    
    try:
        # Initialize database connection
        await init_db()
        
        # Create all tables
        await create_tables()
        
        print("✅ Database setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Database setup failed: {str(e)}")
        print("\n🔍 Common solutions:")
        print("1. Make sure PostgreSQL is running: sudo systemctl start postgresql")
        print("2. Check if database exists: createdb skypost_db")
        print("3. Verify .env file has correct DATABASE_URL")
        print("4. Install asyncpg: pip install asyncpg")
        
    finally:
        await close_db()

async def reset_database():
    """Reset the database (drop and recreate tables)."""
    print("🔧 Resetting database...")
    
    try:
        # Initialize database connection
        await init_db()
        
        # Drop all tables
        await drop_tables()
        
        # Create all tables
        await create_tables()
        
        print("✅ Database reset completed successfully!")
        
    except Exception as e:
        print(f"❌ Database reset failed: {str(e)}")
        
    finally:
        await close_db()

async def create_sample_users():
    """Create sample users for testing."""
    print("👥 Creating sample users...")
    
    try:
        await init_db()
        
        # Create sample users
        user1 = await User.create_user(
            email="john@example.com",
            password="password123",
            first_name="John",
            last_name="Doe"
        )
        
        user2 = await User.create_user(
            email="jane@example.com",
            password="password123",
            first_name="Jane",
            last_name="Smith"
        )
        
        print(f"✅ Created users: {user1.email}, {user2.email}")
        
    except Exception as e:
        print(f"❌ Failed to create sample users: {str(e)}")
        
    finally:
        await close_db()

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python db_setup.py [setup|reset|sample_users]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "setup":
        asyncio.run(setup_database())
    elif command == "reset":
        asyncio.run(reset_database())
    elif command == "sample_users":
        asyncio.run(create_sample_users())
    else:
        print("Invalid command. Use: setup, reset, or sample_users")
        sys.exit(1)

if __name__ == "__main__":
    main()
