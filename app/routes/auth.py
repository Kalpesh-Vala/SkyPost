"""
Authentication routes
"""

from sanic import Blueprint
from sanic.response import json
from pydantic import ValidationError

from app.services.auth_service import AuthService
from app.middleware.auth import jwt_required
from app.utils.responses import success_response, error_response
from app.utils.validation import UserProfileUpdateSchema

# Create authentication blueprint
bp = Blueprint('auth', url_prefix='/auth')

@bp.post('/register')
async def register(request):
    """Register a new user."""
    try:
        data = request.json
        
        # Extract required fields
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        
        # Validate required fields
        if not all([email, password, first_name, last_name]):
            return json(*error_response("All fields are required: email, password, first_name, last_name"))
        
        # Register user
        result = await AuthService.register_user(email, password, first_name, last_name)
        
        return json(*success_response(result, "User registered successfully", 201))
        
    except ValueError as e:
        return json(*error_response(str(e)))
    except Exception as e:
        print(f"Registration error: {str(e)}")  # Debug logging
        return json(*error_response(f"Registration failed: {str(e)}"))

@bp.post('/login')
async def login(request):
    """Login user and return JWT token."""
    try:
        data = request.json
        
        # Extract required fields
        email = data.get('email')
        password = data.get('password')
        
        # Validate required fields
        if not all([email, password]):
            return json(*error_response("Email and password are required"))
        
        # Login user
        result = await AuthService.login_user(email, password)
        
        return json(*success_response(result, "Login successful"))
        
    except ValueError as e:
        return json(*error_response(str(e)))
    except Exception as e:
        print(f"Login error: {str(e)}")  # Debug logging
        return json(*error_response(f"Login failed: {str(e)}"))

@bp.get('/me')
@jwt_required
async def get_profile(request):
    """Get current user profile."""
    try:
        user_id = request.ctx.user_id
        result = await AuthService.get_user_profile(user_id)
        
        return json(*success_response(result, "Profile retrieved successfully"))
        
    except ValueError as e:
        return json(*error_response(str(e)))
    except Exception as e:
        return json(*error_response("Failed to retrieve profile"))

@bp.get('/profile')
@jwt_required  
async def get_profile_alias(request):
    """Get current user profile (alias for /me)."""
    try:
        user_id = request.ctx.user_id
        result = await AuthService.get_user_profile(user_id)
        
        return json(*success_response(result, "Profile retrieved successfully"))
        
    except ValueError as e:
        return json(*error_response(str(e)))
    except Exception as e:
        return json(*error_response("Failed to retrieve profile"))

@bp.put('/me')
@jwt_required
async def update_profile(request):
    """Update current user profile."""
    try:
        user_id = request.ctx.user_id
        data = request.json or {}
        
        # Validate input data
        try:
            validated_data = UserProfileUpdateSchema(**data)
        except ValidationError as e:
            return json(*error_response(f"Validation error: {str(e)}"))
        
        # Extract non-None values for update
        update_data = {
            key: value for key, value in validated_data.dict().items() 
            if value is not None
        }
        
        if not update_data:
            return json(*error_response("No valid fields to update"))
        
        result = await AuthService.update_user_profile(user_id, **update_data)
        
        return json(*success_response(result, "Profile updated successfully"))
        
    except ValueError as e:
        return json(*error_response(str(e)))
    except Exception as e:
        print(f"Profile update error: {str(e)}")  # Add logging for debugging
        return json(*error_response("Failed to update profile"))

@bp.put('/profile')
@jwt_required  
async def update_profile_alias(request):
    """Update current user profile (alias for /me)."""
    try:
        user_id = request.ctx.user_id
        data = request.json or {}
        
        # Validate input data
        try:
            validated_data = UserProfileUpdateSchema(**data)
        except ValidationError as e:
            return json(*error_response(f"Validation error: {str(e)}"))
        
        # Extract non-None values for update
        update_data = {
            key: value for key, value in validated_data.dict().items() 
            if value is not None
        }
        
        if not update_data:
            return json(*error_response("No valid fields to update"))
        
        result = await AuthService.update_user_profile(user_id, **update_data)
        
        return json(*success_response(result, "Profile updated successfully"))
        
    except ValueError as e:
        return json(*error_response(str(e)))
    except Exception as e:
        print(f"Profile update error: {str(e)}")  # Add logging for debugging
        return json(*error_response("Failed to update profile"))

@bp.post('/change-password')
@jwt_required
async def change_password(request):
    """Change user password."""
    try:
        user_id = request.ctx.user_id
        data = request.json
        
        # Extract required fields
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        # Validate required fields
        if not all([current_password, new_password]):
            return json(*error_response("Current password and new password are required"))
        
        result = await AuthService.change_password(user_id, current_password, new_password)
        
        return json(*success_response(result, "Password changed successfully"))
        
    except ValueError as e:
        return json(*error_response(str(e)))
    except Exception as e:
        return json(*error_response("Failed to change password"))

@bp.get('/validate-token')
@jwt_required
async def validate_token(request):
    """Validate JWT token."""
    try:
        user = request.ctx.user
        
        return json(*success_response({
            "valid": True,
            "user": user.to_dict()
        }, "Token is valid"))
        
    except Exception as e:
        return json(*error_response("Token validation failed"))
