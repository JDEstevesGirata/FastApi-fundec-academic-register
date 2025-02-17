"""User models"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr

class UserRole(str, Enum):
    """Enumeration for user roles."""
    ADMIN = "admin"
    TEACHER = "teacher"

class UserBase(BaseModel):
    """Base model representing a user."""
    name: str
    lastname: str
    identification_number: str
    email: EmailStr
    role: UserRole
    is_active: bool = True

class UserCreate(UserBase):
    """Model for user creation, including password."""
    password: str

class UserUpdate(BaseModel):
    """Model for updating user details."""
    name: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class LoginRequest(BaseModel):
    identification_number: str
    password: str
