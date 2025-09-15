"""
User model using SQLAlchemy Core
"""

from datetime import datetime
from sqlalchemy import Table, Column, Integer, String, DateTime, Boolean, Text, select, insert, update, delete
from sqlalchemy.sql import func
import bcrypt

from app.utils.database import metadata, get_session, get_engine

# Define users table
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

class User:
    """User operations using SQLAlchemy Core."""
    
    @staticmethod
    async def create_user(email: str, password: str, first_name: str, last_name: str):
        """Create a new user with hashed password."""
        password_hash = User.hash_password(password)
        
        async with get_session() as session:
            stmt = insert(users_table).values(
                email=email.lower().strip(),
                password_hash=password_hash,
                first_name=first_name.strip(),
                last_name=last_name.strip()
            )
            result = await session.execute(stmt)
            await session.commit()
            
            # Get the created user
            user_id = result.inserted_primary_key[0]
            return await User.get_by_id(user_id)
    
    @staticmethod
    async def get_by_email(email: str):
        """Get user by email address."""
        async with get_session() as session:
            stmt = select(users_table).where(users_table.c.email == email.lower().strip())
            result = await session.execute(stmt)
            row = result.fetchone()
            return row._asdict() if row else None
    
    @staticmethod
    async def get_by_id(user_id: int):
        """Get user by ID."""
        async with get_session() as session:
            stmt = select(users_table).where(users_table.c.id == user_id)
            result = await session.execute(stmt)
            row = result.fetchone()
            return row._asdict() if row else None
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against the stored hash."""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )
    
    @staticmethod
    async def update_last_login(user_id: int):
        """Update the last login timestamp."""
        async with get_session() as session:
            stmt = update(users_table).where(
                users_table.c.id == user_id
            ).values(last_login=datetime.utcnow())
            await session.execute(stmt)
            await session.commit()
    
    @staticmethod
    async def update_user(user_id: int, **kwargs):
        """Update user fields."""
        async with get_session() as session:
            stmt = update(users_table).where(
                users_table.c.id == user_id
            ).values(**kwargs)
            await session.execute(stmt)
            await session.commit()
    
    @staticmethod
    async def update_password(user_id: int, new_password_hash: str):
        """Update user password."""
        async with get_session() as session:
            stmt = update(users_table).where(
                users_table.c.id == user_id
            ).values(
                password_hash=new_password_hash,
                updated_at=datetime.utcnow()
            )
            await session.execute(stmt)
            await session.commit()
    
    @staticmethod
    def to_dict(user_data: dict, exclude_fields=None):
        """Convert user data to dictionary, excluding sensitive fields by default."""
        exclude_fields = exclude_fields or ['password_hash']
        return {k: v for k, v in user_data.items() if k not in exclude_fields}
    
    @staticmethod
    def get_full_name(user_data: dict) -> str:
        """Get the user's full name."""
        return f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}"
