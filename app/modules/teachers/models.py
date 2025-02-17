"""
Teacher domain models and schemas for data validation and serialization.
"""

from pydantic import BaseModel, Field, EmailStr
from app.models.base_model import AuditFields, MongoBaseModel

class TeacherBase(BaseModel):
    """Base Teacher fields"""
    name: str = Field(..., min_length=1, max_length=100)
    lastname: str = Field(..., min_length=1, max_length=100)
    identification_number: str = Field(..., min_length=5, max_length=20)
    email: EmailStr
    mobile_phone: str = Field(..., min_length=10, max_length=15)

class TeacherCreate(TeacherBase):
    """Schema for creating a teacher"""
    pass

class TeacherUpdate(TeacherBase):
    """Schema for updating a teacher"""
    name: str | None = None
    lastname: str | None = None
    identification_number: str | None = None
    email: EmailStr | None = None
    mobile_phone: str | None = None

class Teacher(TeacherBase, MongoBaseModel, AuditFields):
    """Complete Teacher model"""
    pass