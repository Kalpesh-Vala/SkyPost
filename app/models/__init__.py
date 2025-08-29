"""
Database models
"""

from app.models.user import User, users_table
from app.models.message import Message, messages_table
from app.models.attachment import Attachment, attachments_table

__all__ = ['User', 'Message', 'Attachment', 'users_table', 'messages_table', 'attachments_table']
