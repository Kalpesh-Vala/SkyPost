"""
Standard API response utilities
"""

from typing import Any, Dict, Optional
from sanic.response import JSONResponse

def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200
) -> tuple[Dict[str, Any], int]:
    """Create a success response."""
    response = {
        "success": True,
        "message": message
    }
    
    if data is not None:
        response["data"] = data
    
    return response, status_code

def error_response(
    message: str = "Error occurred",
    error_code: Optional[str] = None,
    status_code: int = 400
) -> tuple[Dict[str, Any], int]:
    """Create an error response."""
    response = {
        "success": False,
        "message": message
    }
    
    if error_code:
        response["error_code"] = error_code
    
    return response, status_code

def paginated_response(
    data: list,
    page: int,
    per_page: int,
    total: int,
    message: str = "Success"
) -> tuple[Dict[str, Any], int]:
    """Create a paginated response."""
    total_pages = (total + per_page - 1) // per_page
    
    response = {
        "success": True,
        "message": message,
        "data": data,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }
    
    return response, 200
