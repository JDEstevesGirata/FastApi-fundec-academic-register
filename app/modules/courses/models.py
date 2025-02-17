"""
Course domain models and schemas for data validation and serialization.
"""

from pydantic import BaseModel, Field
from app.models.base_model import AuditFields, MongoBaseModel

class CourseBase(BaseModel):
    """Base Course fields"""
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=20)
    description: str = Field(..., min_length=1, max_length=500)

class CourseCreate(CourseBase):
    """Schema for creating a course"""
    pass

class CourseUpdate(CourseBase):
    """Schema for updating a course"""
    name: str | None = None
    code: str | None = None
    description: str | None = None

class Course(CourseBase, MongoBaseModel, AuditFields):
    """Complete Course model"""
    pass
