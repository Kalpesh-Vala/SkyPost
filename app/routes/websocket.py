"""
WebSocket routes for real-time notifications
"""

import json as json_lib
from sanic import Blueprint
from sanic.response import json
import asyncio
from typing import Dict, Set

from app.middleware.auth import JWTAuth
from app.models.user import User
from app.utils.responses import error_response

# Create websocket blueprint
bp = Blueprint('websocket', url_prefix='/ws')

# Store active WebSocket connections
# In production, use Redis or similar for multi-instance support
active_connections: Dict[int, Set] = {}

class NotificationManager:
    """Manager for WebSocket notifications."""
    
    @staticmethod
    async def add_connection(user_id: int, websocket):
        """Add a WebSocket connection for a user."""
        if user_id not in active_connections:
            active_connections[user_id] = set()
        active_connections[user_id].add(websocket)
        print(f"✅ User {user_id} connected to WebSocket")
    
    @staticmethod
    async def remove_connection(user_id: int, websocket):
        """Remove a WebSocket connection for a user."""
        if user_id in active_connections:
            active_connections[user_id].discard(websocket)
            if not active_connections[user_id]:
                del active_connections[user_id]
        print(f"❌ User {user_id} disconnected from WebSocket")
    
    @staticmethod
    async def notify_user(user_id: int, message: dict):
        """Send a notification to a specific user."""
        if user_id in active_connections:
            disconnected = set()
            
            for websocket in active_connections[user_id].copy():
                try:
                    await websocket.send(json_lib.dumps(message))
                except Exception as e:
                    print(f"Failed to send notification to user {user_id}: {str(e)}")
                    disconnected.add(websocket)
            
            # Remove disconnected websockets
            for ws in disconnected:
                active_connections[user_id].discard(ws)
    
    @staticmethod
    async def notify_new_message(recipient_id: int, sender_name: str, subject: str, message_id: int):
        """Send new message notification."""
        notification = {
            "type": "new_message",
            "data": {
                "message_id": message_id,
                "sender_name": sender_name,
                "subject": subject,
                "timestamp": asyncio.get_event_loop().time()
            },
            "message": f"New message from {sender_name}: {subject}"
        }
        
        await NotificationManager.notify_user(recipient_id, notification)
    
    @staticmethod
    async def get_connection_count(user_id: int = None) -> int:
        """Get the number of active connections."""
        if user_id:
            return len(active_connections.get(user_id, set()))
        return sum(len(connections) for connections in active_connections.values())

@bp.websocket('/notifications')
async def websocket_notifications(request, ws):
    """WebSocket endpoint for real-time notifications."""
    user_id = None
    
    try:
        # Authenticate user via query parameter or initial message
        auth_token = request.args.get('token')
        
        if not auth_token:
            # Wait for authentication message
            auth_message = await ws.recv()
            try:
                auth_data = json_lib.loads(auth_message)
                auth_token = auth_data.get('token')
            except:
                await ws.send(json_lib.dumps({
                    "error": "Invalid authentication message format"
                }))
                return
        
        if not auth_token:
            await ws.send(json_lib.dumps({
                "error": "Authentication token required"
            }))
            return
        
        # Validate token
        try:
            payload = JWTAuth.decode_token(auth_token)
            user = await User.get_by_id(payload['user_id'])
            
            if not user or not user.is_active:
                await ws.send(json_lib.dumps({
                    "error": "Invalid user or user inactive"
                }))
                return
            
            user_id = user.id
            
        except Exception as e:
            await ws.send(json_lib.dumps({
                "error": f"Authentication failed: {str(e)}"
            }))
            return
        
        # Add connection
        await NotificationManager.add_connection(user_id, ws)
        
        # Send welcome message
        await ws.send(json_lib.dumps({
            "type": "connection_established",
            "message": "Connected to notifications",
            "user_id": user_id
        }))
        
        # Keep connection alive and handle incoming messages
        async for message in ws:
            try:
                data = json_lib.loads(message)
                
                # Handle ping/pong for connection keep-alive
                if data.get('type') == 'ping':
                    await ws.send(json_lib.dumps({
                        "type": "pong",
                        "timestamp": asyncio.get_event_loop().time()
                    }))
                
                # Handle other message types if needed
                elif data.get('type') == 'get_stats':
                    connection_count = await NotificationManager.get_connection_count(user_id)
                    await ws.send(json_lib.dumps({
                        "type": "stats",
                        "data": {
                            "active_connections": connection_count,
                            "total_connections": await NotificationManager.get_connection_count()
                        }
                    }))
                
            except json_lib.JSONDecodeError:
                await ws.send(json_lib.dumps({
                    "error": "Invalid JSON message"
                }))
            except Exception as e:
                print(f"Error handling WebSocket message: {str(e)}")
    
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
    
    finally:
        # Clean up connection
        if user_id:
            await NotificationManager.remove_connection(user_id, ws)

@bp.get('/connections')
async def get_connection_stats(request):
    """Get WebSocket connection statistics (for admin/debugging)."""
    try:
        total_connections = await NotificationManager.get_connection_count()
        
        stats = {
            "total_connections": total_connections,
            "users_connected": len(active_connections),
            "connections_per_user": {
                str(user_id): len(connections) 
                for user_id, connections in active_connections.items()
            }
        }
        
        return json({
            "success": True,
            "data": stats
        })
        
    except Exception as e:
        return json(*error_response("Failed to get connection stats"))

# Export the notification manager for use in other parts of the app
notification_manager = NotificationManager()
