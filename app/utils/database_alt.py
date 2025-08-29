"""
Alternative database setup using SQLAlchemy Core with asyncpg
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, Boolean, Text, ForeignKey, BigInteger
from sqlalchemy.sql import func
from config.settings import config

# Create async engine
engine = None
async_session = None
metadata = MetaData()

# Define tables using SQLAlchemy Core
users_table = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('email', String(255), unique=True, nullable=False, index=True),
    Column('password_hash', String(255), nullable=False),
    Column('first_name', String(100), nullable=False),
    Column('last_name', String(100), nullable=False),
    Column('is_active', Boolean, default=True, nullable=False),
    Column('is_verified', Boolean, default=False, nullable=False),
    Column('created_at', DateTime, default=func.now(), nullable=False),
    Column('updated_at', DateTime, default=func.now(), onupdate=func.now(), nullable=False),
    Column('last_login', DateTime, nullable=True),
    Column('profile_picture', String(500), nullable=True),
    Column('bio', Text, nullable=True),
)

messages_table = Table(
    'messages',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('sender_id', Integer, ForeignKey('users.id'), nullable=False, index=True),
    Column('recipient_id', Integer, ForeignKey('users.id'), nullable=True, index=True),
    Column('recipient_email', String(255), nullable=False, index=True),
    Column('sender_email', String(255), nullable=False, index=True),
    Column('subject', String(500), nullable=False),
    Column('body', Text, nullable=False),
    Column('html_body', Text, nullable=True),
    Column('is_read', Boolean, default=False, nullable=False),
    Column('is_draft', Boolean, default=False, nullable=False),
    Column('is_deleted', Boolean, default=False, nullable=False),
    Column('is_spam', Boolean, default=False, nullable=False),
    Column('created_at', DateTime, default=func.now(), nullable=False),
    Column('read_at', DateTime, nullable=True),
    Column('thread_id', String(100), nullable=True, index=True),
)

attachments_table = Table(
    'attachments',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('message_id', Integer, ForeignKey('messages.id'), nullable=False, index=True),
    Column('original_name', String(255), nullable=False),
    Column('stored_name', String(255), nullable=False, unique=True),
    Column('file_path', String(500), nullable=False),
    Column('file_size', BigInteger, nullable=False),
    Column('mime_type', String(100), nullable=False),
    Column('file_extension', String(10), nullable=False),
    Column('uploaded_at', DateTime, default=func.now(), nullable=False),
    Column('is_deleted', Boolean, default=False, nullable=False),
    Column('download_count', Integer, default=0, nullable=False),
)

async def init_db():
    """Initialize database connection."""
    global engine, async_session
    
    # Convert postgresql:// to postgresql+asyncpg://
    database_url = config.DATABASE_URL
    if database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://')
    
    engine = create_async_engine(database_url, echo=config.APP_DEBUG)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    print(f"🔗 Connected to database: {config.DB_NAME}")

async def close_db():
    """Close database connection."""
    global engine
    if engine:
        await engine.dispose()
        print("🔌 Database connection closed")

async def create_tables():
    """Create all database tables."""
    global engine, metadata
    if engine:
        async with engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
        print("📋 Database tables created")

async def drop_tables():
    """Drop all database tables."""
    global engine, metadata
    if engine:
        async with engine.begin() as conn:
            await conn.run_sync(metadata.drop_all)
        print("🗑️ Database tables dropped")

def get_session():
    """Get database session."""
    return async_session()
