"""
Mail/messaging routes
"""

from sanic import Blueprint
from sanic.response import json, file_stream

from app.services.mail_service import MailService
from app.middleware.auth import jwt_required
from app.utils.responses import success_response, error_response, paginated_response

# Create mail blueprint
bp = Blueprint('mail', url_prefix='/mail')

@bp.post('/send')
@jwt_required
async def send_message(request):
    """Send a new message."""
    try:
        user_id = request.ctx.user_id
        data = request.json
        
        # Extract required fields
        to_email = data.get('to_email')
        subject = data.get('subject')
        body = data.get('body')
        message_type = data.get('message_type', 'email')  # Default to 'email' if not provided
        
        # Validate required fields
        if not all([to_email, subject, body]):
            return json(*error_response("to_email, subject, and body are required"))
        
        # Handle file uploads if present
        attachments = []
        if hasattr(request, 'files') and request.files:
            for file_key in request.files:
                file_data = request.files[file_key][0]  # Get first file for each key
                attachments.append({
                    'name': file_data.name,
                    'content': file_data.body,
                    'size': len(file_data.body),
                    'mime_type': file_data.type
                })
        
        # Send message
        result = await MailService.send_message(
            sender_id=user_id,
            to_email=to_email,
            subject=subject,
            body=body,
            message_type=message_type,
            attachments=attachments if attachments else None
        )
        
        return json(*success_response(result, "Message sent successfully", 201))
        
    except ValueError as e:
        return json(*error_response(str(e)))
    except Exception as e:
        return json(*error_response("Failed to send message"))

@bp.get('/inbox')
@jwt_required
async def get_inbox(request):
    """Get inbox messages for the current user."""
    try:
        user_id = request.ctx.user_id
        
        # Extract query parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        search = request.args.get('search')
        
        # Get inbox messages
        result = await MailService.get_inbox(user_id, page, per_page, search)
        
        return json(*paginated_response(
            data=result['messages'],
            page=result['page'],
            per_page=result['per_page'],
            total=result['total_count'],
            message="Inbox retrieved successfully"
        ))
        
    except ValueError as e:
        return json(*error_response(str(e)))
    except Exception as e:
        return json(*error_response("Failed to retrieve inbox"))

@bp.get('/outbox')
@jwt_required
async def get_outbox(request):
    """Get sent messages for the current user."""
    try:
        user_id = request.ctx.user_id
        print(f"Retrieving outbox for user {user_id}")
        
        # Extract query parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        search = request.args.get('search')
        
        # Get outbox messages
        result = await MailService.get_outbox(user_id, page, per_page, search)
        
        return json(*paginated_response(
            data=result['messages'],
            page=result['page'],
            per_page=result['per_page'],
            total=result['total_count'],
            message="Outbox retrieved successfully"
        ))
        
    except ValueError as e:
        print(f"Validation error in outbox: {str(e)}")
        return json(*error_response(str(e)))
    except Exception as e:
        print(f"Error retrieving outbox: {str(e)}")
        # Return empty result set
        return json(*paginated_response(
            data=[],
            page=1,
            per_page=20,
            total=0,
            message="Outbox retrieved successfully"
        ))

@bp.get('/message/<message_id:int>')
@jwt_required
async def get_message(request, message_id):
    """Get a specific message."""
    try:
        user_id = request.ctx.user_id
        print(f"API: Retrieving message {message_id} for user {user_id}")
        
        # Get message
        result = await MailService.get_message(message_id, user_id)
        
        return json(*success_response(result, "Message retrieved successfully"))
        
    except ValueError as e:
        error_msg = str(e)
        print(f"Message retrieval error: {error_msg}")
        
        if "not found" in error_msg.lower():
            return json(*error_response(error_msg, status_code=404))
        elif "access denied" in error_msg.lower():
            return json(*error_response(error_msg, status_code=403))
        elif "deleted" in error_msg.lower():
            return json(*error_response(error_msg, status_code=410))  # Gone
        else:
            return json(*error_response(error_msg))
    except Exception as e:
        print(f"Unexpected error retrieving message {message_id}: {str(e)}")
        return json(*error_response("Failed to retrieve message", status_code=500))

@bp.get('/stats')
@jwt_required
async def get_message_stats(request):
    """Get message statistics for the current user."""
    try:
        user_id = request.ctx.user_id
        
        # Get message stats
        result = await MailService.get_message_stats(user_id)
        
        return json(*success_response(result, "Statistics retrieved successfully"))
        
    except Exception as e:
        return json(*error_response("Failed to retrieve statistics"))

@bp.put('/message/<message_id:int>/read')
@jwt_required
async def mark_message_as_read(request, message_id):
    """Mark a message as read."""
    try:
        user_id = request.ctx.user_id
        
        # Mark as read
        result = await MailService.mark_message_as_read(message_id, user_id)
        
        return json(*success_response(result, "Message marked as read"))
        
    except ValueError as e:
        return json(*error_response(str(e), status_code=404))
    except Exception as e:
        return json(*error_response("Failed to mark message as read"))

@bp.delete('/message/<message_id:int>')
@jwt_required
async def delete_message(request, message_id):
    """Delete a message."""
    try:
        user_id = request.ctx.user_id
        
        # Delete message
        result = await MailService.delete_message(message_id, user_id)
        
        return json(*success_response(result, "Message deleted successfully"))
        
    except ValueError as e:
        return json(*error_response(str(e), status_code=404))
    except Exception as e:
        return json(*error_response("Failed to delete message"))

@bp.get('/attachment/<attachment_id:int>/download')
@jwt_required
async def download_attachment(request, attachment_id):
    """Download an attachment."""
    try:
        user_id = request.ctx.user_id
        
        # Get attachment file path and info
        file_path, original_name, mime_type = await MailService.get_attachment(attachment_id, user_id)
        
        # Return file stream
        return await file_stream(
            file_path,
            filename=original_name,
            mime_type=mime_type
        )
        
    except ValueError as e:
        return json(*error_response(str(e), status_code=404))
    except Exception as e:
        return json(*error_response("Failed to download attachment"))
