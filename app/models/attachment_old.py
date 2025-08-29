"""
Attachment model for storing file metadata
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Boolean, ForeignKey
from sqlalchemy.sql import func

from app.models.base import BaseModel

class Attachment(BaseModel):
    """Attachment model for storing file metadata."""
    
    __tablename__ = 'attachments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey('messages.id'), nullable=False, index=True)
    original_name = Column(String(255), nullable=False)
    stored_name = Column(String(255), nullable=False, unique=True)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)  # Size in bytes
    mime_type = Column(String(100), nullable=False)
    file_extension = Column(String(10), nullable=False)
    uploaded_at = Column(DateTime, default=func.now(), nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    download_count = Column(Integer, default=0, nullable=False)
    
    @classmethod
    async def create_attachment(cls, message_id: int, original_name: str, 
                              stored_name: str, file_path: str, file_size: int, 
                              mime_type: str):
        """Create a new attachment record."""
        file_extension = original_name.split('.')[-1].lower() if '.' in original_name else ''
        
        attachment = await cls.create(
            message_id=message_id,
            original_name=original_name,
            stored_name=stored_name,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            file_extension=file_extension
        )
        
        return attachment
    
    @classmethod
    async def get_by_message_id(cls, message_id: int):
        """Get all attachments for a specific message."""
        return await cls.query.where(
            (cls.message_id == message_id) & 
            (cls.is_deleted == False)
        ).gino.all()
    
    @classmethod
    async def get_by_id(cls, attachment_id: int):
        """Get attachment by ID."""
        return await cls.query.where(
            (cls.id == attachment_id) & 
            (cls.is_deleted == False)
        ).gino.first()
    
    async def increment_download_count(self):
        """Increment the download counter."""
        await self.update(download_count=self.download_count + 1).apply()
    
    async def mark_as_deleted(self):
        """Mark attachment as deleted (soft delete)."""
        await self.update(is_deleted=True).apply()
    
    @property
    def file_size_mb(self) -> float:
        """Get file size in MB."""
        return round(self.file_size / (1024 * 1024), 2)
    
    @property
    def file_size_human(self) -> str:
        """Get human-readable file size."""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def to_dict(self, exclude_fields=None):
        """Convert attachment to dictionary with additional computed fields."""
        exclude_fields = exclude_fields or []
        data = super().to_dict(exclude_fields=exclude_fields)
        data['file_size_human'] = self.file_size_human
        data['file_size_mb'] = self.file_size_mb
        return data
    
    def __repr__(self):
        return f"<Attachment(id={self.id}, name='{self.original_name}', size='{self.file_size_human}')>"
