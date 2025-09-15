"""
Database connection and utilities using modern SQLAlchemy async
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import MetaData
from config.settings import config

# Global database instances
engine = None
async_session = None
metadata = MetaData()

async def init_db():
    """Initialize database connection."""
    global engine, async_session
    
    try:
        # Convert postgresql:// to postgresql+asyncpg://
        database_url = config.DATABASE_URL
        if database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://')
        
        engine = create_async_engine(database_url, echo=config.APP_DEBUG)
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        
        print(f"🔗 Connected to database: {config.DB_NAME}")
    except Exception as e:
        print(f"❌ Failed to connect to database: {str(e)}")
        raise

async def close_db():
    """Close database connection."""
    global engine
    try:
        if engine:
            await engine.dispose()
            print("🔌 Database connection closed")
        else:
            print("🔌 No database connection to close")
    except Exception as e:
        print(f"⚠️  Database close error: {str(e)}")

async def create_tables():
    """Create all database tables."""
    global engine, metadata
    try:
        if engine:
            # Import all models to register them with metadata
            from app.models.user import users_table
            from app.models.message import messages_table
            from app.models.attachment import attachments_table
            
            async with engine.begin() as conn:
                await conn.run_sync(metadata.create_all)
            print("📋 Database tables created")
        else:
            raise Exception("Database engine not initialized")
    except Exception as e:
        print(f"❌ Failed to create tables: {str(e)}")
        raise

async def drop_tables():
    """Drop all database tables."""
    global engine, metadata
    try:
        if engine:
            async with engine.begin() as conn:
                await conn.run_sync(metadata.drop_all)
            print("🗑️ Database tables dropped")
        else:
            raise Exception("Database engine not initialized")
    except Exception as e:
        print(f"❌ Failed to drop tables: {str(e)}")
        raise

def get_session() -> AsyncSession:
    """Get database session."""
    if async_session:
        return async_session()
    else:
        raise Exception("Database session not initialized")

def get_engine():
    """Get database engine."""
    return engine
