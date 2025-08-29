"""
Attachment model using SQLAlchemy Core
"""

from datetime import datetime
from sqlalchemy import Table, Column, Integer, String, DateTime, BigInteger, Boolean, ForeignKey, select, insert, update, func

from app.utils.database import metadata, get_session

# Define attachments table
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

class Attachment:
    """Attachment operations using SQLAlchemy Core."""
    
    @staticmethod
    async def create_attachment(message_id: int, original_name: str, 
                              stored_name: str, file_path: str, file_size: int, 
                              mime_type: str):
        """Create a new attachment record."""
        file_extension = original_name.split('.')[-1].lower() if '.' in original_name else ''
        
        async with get_session() as session:
            stmt = insert(attachments_table).values(
                message_id=message_id,
                original_name=original_name,
                stored_name=stored_name,
                file_path=file_path,
                file_size=file_size,
                mime_type=mime_type,
                file_extension=file_extension
            )
            result = await session.execute(stmt)
            await session.commit()
            
            # Get the created attachment
            attachment_id = result.inserted_primary_key[0]
            return await Attachment.get_by_id_simple(attachment_id)
    
    @staticmethod
    async def get_by_message_id(message_id: int):
        """Get all attachments for a specific message."""
        async with get_session() as session:
            stmt = select(attachments_table).where(
                (attachments_table.c.message_id == message_id) & 
                (attachments_table.c.is_deleted == False)
            )
            result = await session.execute(stmt)
            return [dict(row) for row in result.fetchall()]
    
    @staticmethod
    async def get_by_id(attachment_id: int):
        """Get attachment by ID."""
        async with get_session() as session:
            stmt = select(attachments_table).where(
                (attachments_table.c.id == attachment_id) & 
                (attachments_table.c.is_deleted == False)
            )
            result = await session.execute(stmt)
            row = result.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    async def get_by_id_simple(attachment_id: int):
        """Get attachment by ID without delete check."""
        async with get_session() as session:
            stmt = select(attachments_table).where(attachments_table.c.id == attachment_id)
            result = await session.execute(stmt)
            row = result.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    async def increment_download_count(attachment_id: int):
        """Increment the download counter."""
        async with get_session() as session:
            stmt = update(attachments_table).where(
                attachments_table.c.id == attachment_id
            ).values(download_count=attachments_table.c.download_count + 1)
            await session.execute(stmt)
            await session.commit()
    
    @staticmethod
    async def mark_as_deleted(attachment_id: int):
        """Mark attachment as deleted (soft delete)."""
        async with get_session() as session:
            stmt = update(attachments_table).where(
                attachments_table.c.id == attachment_id
            ).values(is_deleted=True)
            await session.execute(stmt)
            await session.commit()
    
    @staticmethod
    def get_file_size_mb(file_size: int) -> float:
        """Get file size in MB."""
        return round(file_size / (1024 * 1024), 2)
    
    @staticmethod
    def get_file_size_human(file_size: int) -> str:
        """Get human-readable file size."""
        size = file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    @staticmethod
    def to_dict(attachment_data: dict, exclude_fields=None):
        """Convert attachment to dictionary with additional computed fields."""
        exclude_fields = exclude_fields or []
        data = {k: v for k, v in attachment_data.items() if k not in exclude_fields}
        data['file_size_human'] = Attachment.get_file_size_human(attachment_data['file_size'])
        data['file_size_mb'] = Attachment.get_file_size_mb(attachment_data['file_size'])
        return data
