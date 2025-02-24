"""
Course domain models and schemas for data validation and serialization.
"""

from pydantic import BaseModel, Field
from app.models.base_model import AuditFields, MongoBaseModel
from app.utils.mongo import convert_object_id

# Course Models
class CourseBase(BaseModel):
    """Base Course fields"""
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=20)
    description: str = Field(..., min_length=1, max_length=500)

class Course(CourseBase, MongoBaseModel, AuditFields):
    """Complete Course model"""

class CourseCreate(CourseBase):
    """Schema for creating a course"""

class CourseUpdate(CourseBase):
    """Schema for updating a course"""
    name: str | None = None
    code: str | None = None
    description: str | None = None
    is_active: bool

class CourseResponse(CourseBase):
    """Response model for Course with string _id"""
    id: str = Field(alias="_id")

    @classmethod
    def from_mongo(cls, data: dict):
        """Convierte ObjectId a str en la respuesta."""
        return cls(**convert_object_id(data))
