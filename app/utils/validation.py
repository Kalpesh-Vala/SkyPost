"""
Input validation utilities using Pydantic
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime

class UserRegistrationSchema(BaseModel):
    """User registration validation schema."""
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v.strip()

class UserLoginSchema(BaseModel):
    """User login validation schema."""
    email: EmailStr
    password: str

class UserProfileUpdateSchema(BaseModel):
    """User profile update validation schema."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v.strip() if v else v
    
    @validator('bio')
    def validate_bio(cls, v):
        if v is not None and len(v) > 500:
            raise ValueError('Bio cannot exceed 500 characters')
        return v
    
    @validator('profile_picture')
    def validate_profile_picture(cls, v):
        if v is not None and len(v) > 500:
            raise ValueError('Profile picture URL cannot exceed 500 characters')
        return v

class MessageSchema(BaseModel):
    """Message creation validation schema."""
    to_email: EmailStr
    subject: str
    body: str
    
    @validator('subject')
    def validate_subject(cls, v):
        if len(v.strip()) < 1:
            raise ValueError('Subject cannot be empty')
        if len(v) > 200:
            raise ValueError('Subject cannot exceed 200 characters')
        return v.strip()
    
    @validator('body')
    def validate_body(cls, v):
        if len(v.strip()) < 1:
            raise ValueError('Message body cannot be empty')
        return v.strip()

class MessageQuerySchema(BaseModel):
    """Message query validation schema."""
    page: Optional[int] = 1
    per_page: Optional[int] = 20
    search: Optional[str] = None
    
    @validator('page')
    def validate_page(cls, v):
        if v < 1:
            raise ValueError('Page number must be at least 1')
        return v
    
    @validator('per_page')
    def validate_per_page(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Per page must be between 1 and 100')
        return v

def validate_file_upload(file_data: dict) -> bool:
    """Validate file upload data."""
    if not file_data.get('name'):
        return False
    
    # Check file size (assuming file_data has 'size' field)
    max_size = 10 * 1024 * 1024  # 10MB
    if file_data.get('size', 0) > max_size:
        return False
    
    # Check allowed file extensions
    allowed_extensions = {'.pdf', '.doc', '.docx', '.txt', '.jpg', '.jpeg', '.png', '.gif'}
    file_ext = '.' + file_data['name'].split('.')[-1].lower()
    
    return file_ext in allowed_extensions
