"""
Mail service for handling email/messaging operations
"""

import os
import uuid
import aiofiles
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select

from app.models.user import User
from app.models.message import Message, messages_table
from app.models.attachment import Attachment
from app.utils.validation import MessageSchema, MessageQuerySchema, validate_file_upload
from app.utils.database import get_session
from config.settings import config

class MailService:
    """Service class for mail operations."""
    
    @staticmethod
    async def send_message(sender_id: int, to_email: str, subject: str, 
                          body: str, message_type: str = "email", attachments: Optional[List] = None) -> dict:
        """Send a new message."""
        # Validate input
        try:
            message_data = MessageSchema(
                to_email=to_email,
                subject=subject,
                body=body,
                message_type=message_type
            )
        except Exception as e:
            raise ValueError(f"Validation error: {str(e)}")
        
        # Get sender information
        sender = await User.get_by_id(sender_id)
        if not sender:
            raise ValueError("Sender not found")
        
        # Check if recipient exists in our system
        recipient = await User.get_by_email(to_email)
        recipient_id: Optional[int] = recipient['id'] if recipient else None
        
        # Create message
        message = await Message.create_message(
            sender_id=sender_id,
            sender_email=sender['email'],
            recipient_email=message_data.to_email,
            subject=message_data.subject,
            body=message_data.body,
            recipient_id=recipient_id
        )
        
        if not message:
            raise ValueError("Failed to create message")
            
        # Handle attachments if provided
        attachment_results = []
        if attachments and message:
            for attachment in attachments:
                try:
                    attachment_result = await MailService._save_attachment(message['id'], attachment)
                    attachment_results.append(attachment_result)
                except Exception as e:
                    print(f"Failed to save attachment: {str(e)}")
        
        return {
            "message": message,
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
        messages = await Message.get_inbox_messages(user_id, query_data.page or 1, query_data.per_page or 20)
        total_count = await Message.count_inbox_messages(user_id)
        
        # Convert to dictionaries and add attachment info
        message_list = []
        for message in messages:
            # message is already a dict from the model
            message_dict = message.copy()
            attachments = await Attachment.get_by_message_id(message['id'])
            message_dict['attachments'] = attachments  # attachments are already dicts
            message_dict['attachment_count'] = len(attachments)
            message_list.append(message_dict)
        
        per_page_value = query_data.per_page or 20
        total_count_value = total_count or 0
        
        return {
            "messages": message_list,
            "total_count": total_count_value,
            "page": query_data.page or 1,
            "per_page": per_page_value,
            "total_pages": (total_count_value + per_page_value - 1) // per_page_value
        }
    
    @staticmethod
    async def get_outbox(user_id: int, page: int = 1, per_page: int = 20, 
                        search: Optional[str] = None) -> dict:
        """Get sent messages for a user."""
        try:
            # Validate query parameters
            try:
                query_data = MessageQuerySchema(page=page, per_page=per_page, search=search)
            except Exception as e:
                raise ValueError(f"Validation error: {str(e)}")
            
            # Get messages
            messages = await Message.get_outbox_messages(user_id, query_data.page or 1, query_data.per_page or 20)
            total_count = await Message.count_outbox_messages(user_id)
            
            # Convert to dictionaries and add attachment info
            message_list = []
            for message in messages:
                try:
                    # message is already a dict from the model
                    message_dict = message.copy()
                    attachments = await Attachment.get_by_message_id(message['id'])
                    message_dict['attachments'] = attachments or []  # attachments are already dicts
                    message_dict['attachment_count'] = len(attachments) if attachments else 0
                    message_list.append(message_dict)
                except Exception as e:
                    print(f"Error processing message {message.get('id', 'unknown')}: {str(e)}")
                    continue
            
            per_page_value = query_data.per_page or 20
            total_count_value = total_count or 0
            
            return {
                "messages": message_list,
                "total_count": total_count_value,
                "page": query_data.page or 1,
                "per_page": per_page_value,
                "total_pages": max(1, (total_count_value + per_page_value - 1) // per_page_value)
            }
        except Exception as e:
            print(f"Error in get_outbox: {str(e)}")
            # Return empty result set instead of raising an exception
            return {
                "messages": [],
                "total_count": 0,
                "page": page,
                "per_page": per_page,
                "total_pages": 1
            }
    
    @staticmethod
    async def get_message(message_id: int, user_id: int) -> dict:
        """Get a specific message."""
        try:
            print(f"MailService: Attempting to get message {message_id} for user {user_id}")
            # Get the message
            message = await Message.get_by_id(message_id, user_id)
            
            if not message:
                # Try to get more detailed information about why access was denied
                async with get_session() as session:
                    check_stmt = select(messages_table).where(
                        (messages_table.c.id == message_id)
                    )
                    check_result = await session.execute(check_stmt)
                    check_row = check_result.fetchone()
                    
                    if check_row is None:
                        print(f"Message {message_id} does not exist in database")
                        raise ValueError(f"Message with ID {message_id} not found")
                    else:
                        # Convert row to dictionary safely
                        msg_data = {}
                        for column, value in check_row._mapping.items():
                            if isinstance(column, str):
                                msg_data[column] = value
                            else:
                                msg_data[column.name] = value
                                
                        if msg_data.get('is_deleted'):
                            raise ValueError(f"Message with ID {message_id} has been deleted")
                        elif msg_data.get('sender_id') != user_id and msg_data.get('recipient_id') != user_id:
                            print(f"Access denied: User {user_id} attempted to access message {message_id} " +
                                  f"with sender {msg_data.get('sender_id')} and recipient {msg_data.get('recipient_id')}")
                            raise ValueError(f"Access denied to message {message_id}")
                        else:
                            raise ValueError(f"Message not found or access denied for unknown reason")
            
            # Mark as read if user is the recipient
            if message.get('recipient_id') == user_id and not message.get('is_read', False):
                try:
                    await Message.mark_as_read(message_id)
                except Exception as e:
                    print(f"Warning: Failed to mark message {message_id} as read: {str(e)}")
            
            # Get attachments
            try:
                attachments = await Attachment.get_by_message_id(message['id'])
            except Exception as e:
                print(f"Warning: Failed to retrieve attachments for message {message_id}: {str(e)}")
                attachments = []
            
            # Create a copy to avoid modifying the original
            message_dict = message.copy()
            message_dict['attachments'] = attachments or []
            message_dict['attachment_count'] = len(attachments) if attachments else 0
            
            return {
                "message": message_dict
            }
        except ValueError as e:
            # Re-raise ValueError for proper 404 handling
            raise
        except Exception as e:
            print(f"Error retrieving message {message_id}: {str(e)}")
            raise ValueError(f"Failed to retrieve message: {str(e)}")
    
    @staticmethod
    async def get_message_stats(user_id: int) -> dict:
        """Get message statistics for a user."""
        inbox_count = await Message.count_inbox_messages(user_id)
        outbox_count = await Message.count_outbox_messages(user_id)
        unread_count = await Message.count_unread_messages(user_id)
        
        # Handle potential None values
        inbox_count = inbox_count or 0
        outbox_count = outbox_count or 0
        unread_count = unread_count or 0
        
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
        
        if message['recipient_id'] != user_id:
            raise ValueError("Only recipients can mark messages as read")
        
        await Message.mark_as_read(message_id)
        
        return {
            "message": "Message marked as read"
        }
    
    @staticmethod
    async def delete_message(message_id: int, user_id: int) -> dict:
        """Delete a message (soft delete)."""
        message = await Message.get_by_id(message_id, user_id)
        if not message:
            raise ValueError("Message not found or access denied")
        
        await Message.mark_as_deleted(message_id)
        
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
        
        if not attachment:
            raise ValueError("Failed to create attachment")
        
        return attachment
    
    @staticmethod
    async def get_attachment(attachment_id: int, user_id: int) -> tuple:
        """Get attachment file for download."""
        attachment = await Attachment.get_by_id(attachment_id)
        if not attachment:
            raise ValueError("Attachment not found")
        
        # Check if user has access to this attachment's message
        message = await Message.get_by_id(attachment['message_id'], user_id)
        if not message:
            raise ValueError("Access denied")
        
        # Increment download counter
        await Attachment.increment_download_count(attachment_id)
        
        return attachment['file_path'], attachment['original_name'], attachment['mime_type']
