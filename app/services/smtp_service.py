"""
SMTP service for sending real emails (future integration)
"""

import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import aiosmtplib
from typing import List, Optional

from config.settings import config

class SMTPService:
    """Service for sending emails via SMTP."""
    
    def __init__(self):
        self.smtp_host = config.SMTP_HOST
        self.smtp_port = config.SMTP_PORT
        self.smtp_username = config.SMTP_USERNAME
        self.smtp_password = config.SMTP_PASSWORD
        self.smtp_use_tls = config.SMTP_USE_TLS
    
    async def send_email(self, to_email: str, subject: str, body: str, 
                        from_email: str = None, html_body: str = None,
                        attachments: Optional[List[str]] = None) -> bool:
        """
        Send an email via SMTP (async version).
        This is a placeholder for future SMTP integration.
        """
        try:
            # Use configured email as sender if not specified
            from_email = from_email or self.smtp_username
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_email
            msg['To'] = to_email
            
            # Add text body
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML body if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    await self._attach_file(msg, file_path)
            
            # Send email using aiosmtplib for async operation
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                start_tls=self.smtp_use_tls,
                username=self.smtp_username,
                password=self.smtp_password,
            )
            
            return True
            
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False
    
    async def _attach_file(self, msg: MIMEMultipart, file_path: str):
        """Attach a file to the email message."""
        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {file_path.split("/")[-1]}',
            )
            
            msg.attach(part)
        except Exception as e:
            print(f"Failed to attach file {file_path}: {str(e)}")
    
    async def mock_send_email(self, to_email: str, subject: str, body: str, 
                             from_email: str = None) -> bool:
        """
        Mock email sending function for development/testing.
        This simulates sending an email without actually sending it.
        """
        print("📧 MOCK EMAIL SENT:")
        print(f"   From: {from_email or self.smtp_username}")
        print(f"   To: {to_email}")
        print(f"   Subject: {subject}")
        print(f"   Body: {body[:100]}{'...' if len(body) > 100 else ''}")
        print("   Status: ✅ Successfully sent (mock)")
        
        # Simulate some async delay
        await asyncio.sleep(0.1)
        
        return True
    
    async def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """Send welcome email to new users."""
        subject = f"Welcome to {config.APP_NAME}!"
        body = f"""
        Hi {user_name},
        
        Welcome to {config.APP_NAME}! Your account has been successfully created.
        
        You can now start sending and receiving messages through our platform.
        
        Best regards,
        The {config.APP_NAME} Team
        """
        
        # Use mock for development, switch to real SMTP in production
        return await self.mock_send_email(user_email, subject, body)
    
    async def send_notification_email(self, user_email: str, user_name: str, 
                                    sender_name: str, subject: str) -> bool:
        """Send new message notification email."""
        notification_subject = f"New message from {sender_name}"
        body = f"""
        Hi {user_name},
        
        You have received a new message on {config.APP_NAME}.
        
        From: {sender_name}
        Subject: {subject}
        
        Login to your account to read the full message.
        
        Best regards,
        The {config.APP_NAME} Team
        """
        
        # Use mock for development, switch to real SMTP in production
        return await self.mock_send_email(user_email, notification_subject, body)

# Global SMTP service instance
smtp_service = SMTPService()
