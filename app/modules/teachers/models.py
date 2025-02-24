"""
Teacher domain models and schemas for data validation and serialization.
"""

from pydantic import BaseModel, Field, EmailStr
from app.models.base_model import AuditFields, MongoBaseModel
from app.utils.mongo import convert_object_id

class TeacherBase(BaseModel):
    """Base Teacher fields"""
    name: str = Field(..., min_length=1, max_length=100)
    lastname: str = Field(..., min_length=1, max_length=100)
    identification_number: str = Field(..., min_length=5, max_length=20)
    email: EmailStr
    mobile_phone: str = Field(..., min_length=8, max_length=15)
    is_active: bool
    role: str
class Teacher(TeacherBase, MongoBaseModel, AuditFields):
    """Complete Teacher model"""

class TeacherCreate(TeacherBase):
    """Schema for creating a teacher"""

class TeacherUpdate(TeacherBase):
    """Schema for updating a teacher"""
    name: str | None = None
    lastname: str | None = None
    identification_number: str | None = None
    email: EmailStr | None = None
    mobile_phone: str | None = None
    is_active: bool
    role: str

class TeacherResponse(TeacherBase):
    """Response model for Teacher with string _id"""
    id: str = Field(alias="_id")

    @classmethod
    def from_mongo(cls, data: dict):
        """Convierte ObjectId a str en la respuesta."""
        return cls(**convert_object_id(data))
    