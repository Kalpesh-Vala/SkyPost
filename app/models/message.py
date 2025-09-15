"""
Message model using SQLAlchemy Core
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Table, Column, Integer, String, DateTime, Boolean, Text, ForeignKey, select, insert, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.database import metadata, get_session, get_engine

# Define messages table
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

class Message:
    """Message operations using SQLAlchemy Core."""
    
    @staticmethod
    async def create_message(sender_id: int, sender_email: str, 
                           recipient_email: str, subject: str, body: str,
                           recipient_id: Optional[int] = None, html_body: Optional[str] = None):
        """Create a new message."""
        async with get_session() as session:
            stmt = insert(messages_table).values(
                sender_id=sender_id,
                sender_email=sender_email.lower().strip(),
                recipient_email=recipient_email.lower().strip(),
                recipient_id=recipient_id,
                subject=subject.strip(),
                body=body,
                html_body=html_body
            )
            result = await session.execute(stmt)
            await session.commit()
            
            # Get the created message
            if result.inserted_primary_key:
                message_id = result.inserted_primary_key[0]
                return await Message.get_by_id_simple(message_id)
            else:
                raise Exception("Failed to create message")
    
    @staticmethod
    async def get_inbox_messages(user_id: int, page: int = 1, per_page: int = 20):
        """Get inbox messages for a user."""
        offset = (page - 1) * per_page
        
        async with get_session() as session:
            stmt = select(messages_table).where(
                (messages_table.c.recipient_id == user_id) & 
                (messages_table.c.is_deleted == False) & 
                (messages_table.c.is_draft == False)
            ).order_by(messages_table.c.created_at.desc()).offset(offset).limit(per_page)
            
            result = await session.execute(stmt)
            return [dict(row) for row in result.fetchall()]
    
    @staticmethod
    async def get_outbox_messages(user_id: int, page: int = 1, per_page: int = 20):
        """Get sent messages for a user."""
        offset = (page - 1) * per_page
        
        async with get_session() as session:
            stmt = select(messages_table).where(
                (messages_table.c.sender_id == user_id) & 
                (messages_table.c.is_deleted == False) & 
                (messages_table.c.is_draft == False)
            ).order_by(messages_table.c.created_at.desc()).offset(offset).limit(per_page)
            
            result = await session.execute(stmt)
            return [dict(row) for row in result.fetchall()]
    
    @staticmethod
    async def get_by_id(message_id: int, user_id: int):
        """Get a message by ID if user has access."""
        async with get_session() as session:
            stmt = select(messages_table).where(
                (messages_table.c.id == message_id) & 
                ((messages_table.c.sender_id == user_id) | (messages_table.c.recipient_id == user_id)) &
                (messages_table.c.is_deleted == False)
            )
            result = await session.execute(stmt)
            row = result.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    async def get_by_id_simple(message_id: int):
        """Get a message by ID without access check."""
        async with get_session() as session:
            stmt = select(messages_table).where(messages_table.c.id == message_id)
            result = await session.execute(stmt)
            row = result.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    async def count_inbox_messages(user_id: int):
        """Count total inbox messages for a user."""
        async with get_session() as session:
            stmt = select(func.count(messages_table.c.id)).where(
                (messages_table.c.recipient_id == user_id) & 
                (messages_table.c.is_deleted == False) & 
                (messages_table.c.is_draft == False)
            )
            result = await session.execute(stmt)
            return result.scalar()
    
    @staticmethod
    async def count_outbox_messages(user_id: int):
        """Count total sent messages for a user."""
        async with get_session() as session:
            stmt = select(func.count(messages_table.c.id)).where(
                (messages_table.c.sender_id == user_id) & 
                (messages_table.c.is_deleted == False) & 
                (messages_table.c.is_draft == False)
            )
            result = await session.execute(stmt)
            return result.scalar()
    
    @staticmethod
    async def count_unread_messages(user_id: int):
        """Count unread messages for a user."""
        async with get_session() as session:
            stmt = select(func.count(messages_table.c.id)).where(
                (messages_table.c.recipient_id == user_id) & 
                (messages_table.c.is_read == False) & 
                (messages_table.c.is_deleted == False) & 
                (messages_table.c.is_draft == False)
            )
            result = await session.execute(stmt)
            return result.scalar()
    
    @staticmethod
    async def mark_as_read(message_id: int):
        """Mark message as read."""
        async with get_session() as session:
            stmt = update(messages_table).where(
                messages_table.c.id == message_id
            ).values(
                is_read=True, 
                read_at=datetime.utcnow()
            )
            await session.execute(stmt)
            await session.commit()
    
    @staticmethod
    async def mark_as_deleted(message_id: int):
        """Mark message as deleted (soft delete)."""
        async with get_session() as session:
            stmt = update(messages_table).where(
                messages_table.c.id == message_id
            ).values(is_deleted=True)
            await session.execute(stmt)
            await session.commit()
    
    @staticmethod
    async def mark_as_spam(message_id: int):
        """Mark message as spam."""
        async with get_session() as session:
            stmt = update(messages_table).where(
                messages_table.c.id == message_id
            ).values(is_spam=True)
            await session.execute(stmt)
            await session.commit()
