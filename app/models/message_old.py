"""
Message model for storing email messages
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func

from app.models.base import BaseModel

class Message(BaseModel):
    """Message model for storing email messages."""
    
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    recipient_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    recipient_email = Column(String(255), nullable=False, index=True)
    sender_email = Column(String(255), nullable=False, index=True)
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    html_body = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    is_draft = Column(Boolean, default=False, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    is_spam = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    read_at = Column(DateTime, nullable=True)
    thread_id = Column(String(100), nullable=True, index=True)  # For message threading
    
    @classmethod
    async def create_message(cls, sender_id: int, sender_email: str, 
                           recipient_email: str, subject: str, body: str,
                           recipient_id: int = None, html_body: str = None):
        """Create a new message."""
        message = await cls.create(
            sender_id=sender_id,
            sender_email=sender_email.lower().strip(),
            recipient_email=recipient_email.lower().strip(),
            recipient_id=recipient_id,
            subject=subject.strip(),
            body=body,
            html_body=html_body
        )
        
        return message
    
    @classmethod
    async def get_inbox_messages(cls, user_id: int, page: int = 1, per_page: int = 20):
        """Get inbox messages for a user."""
        offset = (page - 1) * per_page
        
        messages = await cls.query.where(
            (cls.recipient_id == user_id) & 
            (cls.is_deleted == False) & 
            (cls.is_draft == False)
        ).order_by(cls.created_at.desc()).offset(offset).limit(per_page).gino.all()
        
        return messages
    
    @classmethod
    async def get_outbox_messages(cls, user_id: int, page: int = 1, per_page: int = 20):
        """Get sent messages for a user."""
        offset = (page - 1) * per_page
        
        messages = await cls.query.where(
            (cls.sender_id == user_id) & 
            (cls.is_deleted == False) & 
            (cls.is_draft == False)
        ).order_by(cls.created_at.desc()).offset(offset).limit(per_page).gino.all()
        
        return messages
    
    @classmethod
    async def get_by_id(cls, message_id: int, user_id: int):
        """Get a message by ID if user has access."""
        return await cls.query.where(
            (cls.id == message_id) & 
            ((cls.sender_id == user_id) | (cls.recipient_id == user_id)) &
            (cls.is_deleted == False)
        ).gino.first()
    
    @classmethod
    async def count_inbox_messages(cls, user_id: int):
        """Count total inbox messages for a user."""
        return await cls.query.where(
            (cls.recipient_id == user_id) & 
            (cls.is_deleted == False) & 
            (cls.is_draft == False)
        ).gino.scalar(func.count())
    
    @classmethod
    async def count_outbox_messages(cls, user_id: int):
        """Count total sent messages for a user."""
        return await cls.query.where(
            (cls.sender_id == user_id) & 
            (cls.is_deleted == False) & 
            (cls.is_draft == False)
        ).gino.scalar(func.count())
    
    @classmethod
    async def count_unread_messages(cls, user_id: int):
        """Count unread messages for a user."""
        return await cls.query.where(
            (cls.recipient_id == user_id) & 
            (cls.is_read == False) & 
            (cls.is_deleted == False) & 
            (cls.is_draft == False)
        ).gino.scalar(func.count())
    
    async def mark_as_read(self):
        """Mark message as read."""
        if not self.is_read:
            await self.update(
                is_read=True, 
                read_at=datetime.utcnow()
            ).apply()
    
    async def mark_as_deleted(self):
        """Mark message as deleted (soft delete)."""
        await self.update(is_deleted=True).apply()
    
    async def mark_as_spam(self):
        """Mark message as spam."""
        await self.update(is_spam=True).apply()
    
    def __repr__(self):
        return f"<Message(id={self.id}, subject='{self.subject[:30]}...', from='{self.sender_email}', to='{self.recipient_email}')>"
