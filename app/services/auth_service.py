"""
Authentication service for user management
"""

from datetime import datetime
from app.models.user import User
from app.middleware.auth import JWTAuth
from app.utils.validation import UserRegistrationSchema, UserLoginSchema

class AuthService:
    """Service class for authentication operations."""
    
    @staticmethod
    async def register_user(email: str, password: str, first_name: str, last_name: str) -> dict:
        """Register a new user."""
        # Validate input
        try:
            user_data = UserRegistrationSchema(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
        except Exception as e:
            raise ValueError(f"Validation error: {str(e)}")
        
        # Check if user already exists
        existing_user = await User.get_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Create new user
        user = await User.create_user(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        
        # Generate JWT token
        token = JWTAuth.generate_token(user.id, user.email)
        
        return {
            "user": user.to_dict(),
            "token": token,
            "message": "User registered successfully"
        }
    
    @staticmethod
    async def login_user(email: str, password: str) -> dict:
        """Authenticate user and return token."""
        # Validate input
        try:
            login_data = UserLoginSchema(email=email, password=password)
        except Exception as e:
            raise ValueError(f"Validation error: {str(e)}")
        
        # Get user by email
        user = await User.get_by_email(login_data.email)
        if not user:
            raise ValueError("Invalid email or password")
        
        # Check if user is active
        if not user.is_active:
            raise ValueError("Account is deactivated")
        
        # Verify password
        if not user.verify_password(login_data.password):
            raise ValueError("Invalid email or password")
        
        # Update last login
        await user.update_last_login()
        
        # Generate JWT token
        token = JWTAuth.generate_token(user.id, user.email)
        
        return {
            "user": user.to_dict(),
            "token": token,
            "message": "Login successful"
        }
    
    @staticmethod
    async def get_user_profile(user_id: int) -> dict:
        """Get user profile information."""
        user = await User.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        return {
            "user": user.to_dict(),
            "message": "Profile retrieved successfully"
        }
    
    @staticmethod
    async def update_user_profile(user_id: int, **kwargs) -> dict:
        """Update user profile information."""
        user = await User.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Filter allowed fields for update
        allowed_fields = ['first_name', 'last_name', 'bio', 'profile_picture']
        update_data = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}
        
        if update_data:
            await user.update(**update_data).apply()
        
        return {
            "user": user.to_dict(),
            "message": "Profile updated successfully"
        }
    
    @staticmethod
    async def change_password(user_id: int, current_password: str, new_password: str) -> dict:
        """Change user password."""
        user = await User.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Verify current password
        if not user.verify_password(current_password):
            raise ValueError("Current password is incorrect")
        
        # Validate new password
        if len(new_password) < 8:
            raise ValueError("New password must be at least 8 characters long")
        
        # Update password
        new_password_hash = User.hash_password(new_password)
        await user.update(password_hash=new_password_hash).apply()
        
        return {
            "message": "Password changed successfully"
        }
