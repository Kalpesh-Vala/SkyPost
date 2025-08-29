"""
Base model configuration
"""

from app.utils.database import db

class BaseModel(db.Model):
    """Base model with common fields and utilities."""
    __abstract__ = True
    
    def to_dict(self, exclude_fields=None):
        """Convert model instance to dictionary."""
        exclude_fields = exclude_fields or []
        result = {}
        
        for column in self.__table__.columns:
            if column.name not in exclude_fields:
                value = getattr(self, column.name)
                # Convert datetime to ISO string for JSON serialization
                if hasattr(value, 'isoformat'):
                    value = value.isoformat()
                result[column.name] = value
        
        return result
