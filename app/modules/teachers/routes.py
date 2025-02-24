"""Teacher routes"""

from typing import List
from fastapi import APIRouter, Depends, Path
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.dependencies import get_database
from app.exceptions.http_exceptions import NotFoundException
from app.modules.teachers.services import TeacherService
from app.modules.teachers.models import Teacher, TeacherCreate, TeacherUpdate
from app.utils.security import check_admin_role

teacher_router = APIRouter(prefix="/teachers", tags=["teachers"])

def get_teacher_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> TeacherService:
    """Dependency to provide TeacherService"""
    return TeacherService(db)

@teacher_router.post("/", response_model=Teacher)
async def create_teacher(
    data: TeacherCreate,
    service: TeacherService = Depends(get_teacher_service),
    user: str = Depends(check_admin_role),
):
    """Create a new teacher"""
    return await service.create_teacher(data, user.identification_number)

@teacher_router.get("/{teacher_id}", response_model=Teacher)
async def get_teacher(
    teacher_id: str = Path(..., title="The ID of the teacher to get"),
    service: TeacherService = Depends(get_teacher_service),
    user: str = Depends(check_admin_role),
):
    """Get a specific teacher by ID"""
    return await service.get_by_id_or_raise(teacher_id, "Teacher")

@teacher_router.get("/", response_model=List[Teacher])
async def list_teachers(
    skip: int = 0,
    limit: int = 100,
    service: TeacherService = Depends(get_teacher_service),
    user: str = Depends(check_admin_role),
):
    """List all teachers with pagination"""
    return await service.get_all(skip, limit)

@teacher_router.put("/{teacher_id}", response_model=Teacher)
async def update_teacher(
    data: TeacherUpdate,
    teacher_id: str = Path(..., title="The ID of the teacher to update"),
    service: TeacherService = Depends(get_teacher_service),
    user: str = Depends(check_admin_role),
):
    """Update a specific teacher"""
    return await service.update_teacher(teacher_id, data, user.identification_number)

@teacher_router.delete("/{teacher_id}")
async def delete_teacher(
    teacher_id: str = Path(..., title="The ID of the teacher to delete"),
    service: TeacherService = Depends(get_teacher_service),
    user: str = Depends(check_admin_role),
):
    """Soft delete a teacher"""
    success = await service.delete_teacher(teacher_id, user)
    if not success:
        raise NotFoundException("Teacher", teacher_id)
    return {"message": "Teacher is disabled"}
