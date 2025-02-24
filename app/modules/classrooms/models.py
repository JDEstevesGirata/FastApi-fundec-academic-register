"""
Classroom domain models and schemas for data validation and serialization.
"""

from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.base_model import AuditFields, MongoBaseModel

class ClassroomBase(BaseModel):
    """Base Classroom fields"""
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=20)
    is_active: bool

class Classroom(ClassroomBase, MongoBaseModel, AuditFields):
    """Complete Classroom model"""

class ClassroomCreate(ClassroomBase):
    """Schema for creating a classroom"""

class ClassroomUpdate(ClassroomBase):
    """Schema for updating a classroom"""
    name: str | None = None
    code: str | None = None

class ClassroomResponse(ClassroomBase):
    """Response model for Classroom with string _id"""
    id: str = Field(alias="_id")

    @classmethod
    def from_mongo(cls, data: dict):
        """Convierte ObjectId a str en la respuesta."""
        if "_id" in data and isinstance(data["_id"], ObjectId):
            data["_id"] = str(data["_id"])
        return cls(**data)
    