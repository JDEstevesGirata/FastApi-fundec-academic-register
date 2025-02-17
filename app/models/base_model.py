"""
Base model definitions including audit fields and common functionality
for all domain models in the application.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class AuditFields(BaseModel):
    """Base audit fields that should be included in all models"""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    is_active: bool = True

class MongoBaseModel(BaseModel):
    """Base model with MongoDB id field"""
    id: Optional[str] = Field(None, alias="_id")
