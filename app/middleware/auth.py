"""
JWT Authentication middleware
"""

import jwt
from datetime import datetime, timedelta
from functools import wraps
from sanic.response import json

from config.settings import config
from app.models.user import User
from app.utils.responses import error_response

class JWTAuth:
    """JWT Authentication utilities."""
    
    @staticmethod
    def generate_token(user_id: int, email: str) -> str:
        """Generate JWT token for user."""
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(hours=config.JWT_EXPIRATION_HOURS),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    
    @staticmethod
    def decode_token(token: str) -> dict:
        """Decode and validate JWT token."""
        try:
            payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
    
    @staticmethod
    def extract_token_from_header(auth_header: str) -> str:
        """Extract token from Authorization header."""
        if not auth_header or not auth_header.startswith('Bearer '):
            raise ValueError("Invalid authorization header format")
        
        return auth_header.split(' ')[1]

def jwt_required(f):
    """Decorator to require JWT authentication."""
    @wraps(f)
    async def decorated_function(request, *args, **kwargs):
        try:
            # Extract token from Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return json(*error_response("Authorization header required", status_code=401))
            
            token = JWTAuth.extract_token_from_header(auth_header)
            payload = JWTAuth.decode_token(token)
            
            # Get user from database
            user = await User.get_by_id(payload['user_id'])
            if not user or not user['is_active']:
                return json(*error_response("User not found or inactive", status_code=401))
            
            # Add user to request context
            request.ctx.user = user
            request.ctx.user_id = user['id']
            
        except ValueError as e:
            return json(*error_response(str(e), status_code=401))
        except Exception as e:
            return json(*error_response("Authentication failed", status_code=401))
        
        return await f(request, *args, **kwargs)
    
    return decorated_function

def optional_jwt(f):
    """Decorator for optional JWT authentication."""
    @wraps(f)
    async def decorated_function(request, *args, **kwargs):
        request.ctx.user = None
        request.ctx.user_id = None
        
        try:
            auth_header = request.headers.get('Authorization')
            if auth_header:
                token = JWTAuth.extract_token_from_header(auth_header)
                payload = JWTAuth.decode_token(token)
                
                user = await User.get_by_id(payload['user_id'])
                if user and user['is_active']:
                    request.ctx.user = user
                    request.ctx.user_id = user['id']
        except:
            # If token is invalid, just proceed without authentication
            pass
        
        return await f(request, *args, **kwargs)
    
    return decorated_function
