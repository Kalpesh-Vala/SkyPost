"""
Mail service for handling email/messaging operations
"""

import os
import uuid
import aiofiles
from typing import List, Optional
from datetime import datetime

from app.models.user import User
from app.models.message import Message
from app.models.attachment import Attachment
from app.utils.validation import MessageSchema, MessageQuerySchema, validate_file_upload
from config.settings import config

class MailService:
    """Service class for mail operations."""
    
    @staticmethod
    async def send_message(sender_id: int, to_email: str, subject: str, 
                          body: str, attachments: Optional[List] = None) -> dict:
        """Send a new message."""
        # Validate input
        try:
            message_data = MessageSchema(
                to_email=to_email,
                subject=subject,
                body=body
            )
        except Exception as e:
            raise ValueError(f"Validation error: {str(e)}")
        
        # Get sender information
        sender = await User.get_by_id(sender_id)
        if not sender:
            raise ValueError("Sender not found")
        
        # Check if recipient exists in our system
        recipient = await User.get_by_email(to_email)
        recipient_id = recipient.id if recipient else None
        
        # Create message
        message = await Message.create_message(
            sender_id=sender_id,
            sender_email=sender.email,
            recipient_email=message_data.to_email,
            subject=message_data.subject,
            body=message_data.body,
            recipient_id=recipient_id
        )
        
        # Handle attachments if provided
        attachment_results = []
        if attachments:
            for attachment in attachments:
                try:
                    attachment_result = await MailService._save_attachment(message.id, attachment)
                    attachment_results.append(attachment_result)
                except Exception as e:
                    print(f"Failed to save attachment: {str(e)}")
        
        return {
            "message": message.to_dict(),
            "attachments": attachment_results,
            "message_text": "Message sent successfully"
        }
    
    @staticmethod
    async def get_inbox(user_id: int, page: int = 1, per_page: int = 20, 
                       search: Optional[str] = None) -> dict:
        """Get inbox messages for a user."""
        # Validate query parameters
        try:
            query_data = MessageQuerySchema(page=page, per_page=per_page, search=search)
        except Exception as e:
            raise ValueError(f"Validation error: {str(e)}")
        
        # Get messages
        messages = await Message.get_inbox_messages(user_id, query_data.page, query_data.per_page)
        total_count = await Message.count_inbox_messages(user_id)
        
        # Convert to dictionaries and add attachment info
        message_list = []
        for message in messages:
            message_dict = message.to_dict()
            attachments = await Attachment.get_by_message_id(message.id)
            message_dict['attachments'] = [att.to_dict() for att in attachments]
            message_dict['attachment_count'] = len(attachments)
            message_list.append(message_dict)
        
        return {
            "messages": message_list,
            "total_count": total_count,
            "page": query_data.page,
            "per_page": query_data.per_page,
            "total_pages": (total_count + query_data.per_page - 1) // query_data.per_page
        }
    
    @staticmethod
    async def get_outbox(user_id: int, page: int = 1, per_page: int = 20, 
                        search: Optional[str] = None) -> dict:
        """Get sent messages for a user."""
        # Validate query parameters
        try:
            query_data = MessageQuerySchema(page=page, per_page=per_page, search=search)
        except Exception as e:
            raise ValueError(f"Validation error: {str(e)}")
        
        # Get messages
        messages = await Message.get_outbox_messages(user_id, query_data.page, query_data.per_page)
        total_count = await Message.count_outbox_messages(user_id)
        
        # Convert to dictionaries and add attachment info
        message_list = []
        for message in messages:
            message_dict = message.to_dict()
            attachments = await Attachment.get_by_message_id(message.id)
            message_dict['attachments'] = [att.to_dict() for att in attachments]
            message_dict['attachment_count'] = len(attachments)
            message_list.append(message_dict)
        
        return {
            "messages": message_list,
            "total_count": total_count,
            "page": query_data.page,
            "per_page": query_data.per_page,
            "total_pages": (total_count + query_data.per_page - 1) // query_data.per_page
        }
    
    @staticmethod
    async def get_message(message_id: int, user_id: int) -> dict:
        """Get a specific message."""
        message = await Message.get_by_id(message_id, user_id)
        if not message:
            raise ValueError("Message not found or access denied")
        
        # Mark as read if user is the recipient
        if message.recipient_id == user_id and not message.is_read:
            await message.mark_as_read()
        
        # Get attachments
        attachments = await Attachment.get_by_message_id(message.id)
        
        message_dict = message.to_dict()
        message_dict['attachments'] = [att.to_dict() for att in attachments]
        
        return {
            "message": message_dict
        }
    
    @staticmethod
    async def get_message_stats(user_id: int) -> dict:
        """Get message statistics for a user."""
        inbox_count = await Message.count_inbox_messages(user_id)
        outbox_count = await Message.count_outbox_messages(user_id)
        unread_count = await Message.count_unread_messages(user_id)
        
        return {
            "inbox_count": inbox_count,
            "outbox_count": outbox_count,
            "unread_count": unread_count,
            "total_messages": inbox_count + outbox_count
        }
    
    @staticmethod
    async def mark_message_as_read(message_id: int, user_id: int) -> dict:
        """Mark a message as read."""
        message = await Message.get_by_id(message_id, user_id)
        if not message:
            raise ValueError("Message not found or access denied")
        
        if message.recipient_id != user_id:
            raise ValueError("Only recipients can mark messages as read")
        
        await message.mark_as_read()
        
        return {
            "message": "Message marked as read"
        }
    
    @staticmethod
    async def delete_message(message_id: int, user_id: int) -> dict:
        """Delete a message (soft delete)."""
        message = await Message.get_by_id(message_id, user_id)
        if not message:
            raise ValueError("Message not found or access denied")
        
        await message.mark_as_deleted()
        
        return {
            "message": "Message deleted successfully"
        }
    
    @staticmethod
    async def _save_attachment(message_id: int, file_data: dict) -> dict:
        """Save an attachment file and create database record."""
        # Validate file
        if not validate_file_upload(file_data):
            raise ValueError("Invalid file upload")
        
        # Generate unique filename
        file_extension = file_data['name'].split('.')[-1]
        stored_name = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(config.UPLOAD_FOLDER, stored_name)
        
        # Ensure upload directory exists
        os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
        
        # Save file (assuming file_data has 'content' field with file bytes)
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_data['content'])
        
        # Create database record
        attachment = await Attachment.create_attachment(
            message_id=message_id,
            original_name=file_data['name'],
            stored_name=stored_name,
            file_path=file_path,
            file_size=file_data['size'],
            mime_type=file_data.get('mime_type', 'application/octet-stream')
        )
        
        return attachment.to_dict()
    
    @staticmethod
    async def get_attachment(attachment_id: int, user_id: int) -> tuple:
        """Get attachment file for download."""
        attachment = await Attachment.get_by_id(attachment_id)
        if not attachment:
            raise ValueError("Attachment not found")
        
        # Check if user has access to this attachment's message
        message = await Message.get_by_id(attachment.message_id, user_id)
        if not message:
            raise ValueError("Access denied")
        
        # Increment download counter
        await attachment.increment_download_count()
        
        return attachment.file_path, attachment.original_name, attachment.mime_type
