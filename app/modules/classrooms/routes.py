"""Classrooms routes"""

from typing import List
from fastapi import APIRouter, Depends, Path
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.dependencies import get_database
from app.exceptions.http_exceptions import NotFoundException
from app.modules.classrooms.models import Classroom, ClassroomCreate, ClassroomUpdate
from app.modules.classrooms.service import ClassroomService
from app.utils.security import check_admin_role, check_teacher_role


router = APIRouter(prefix="/classrooms", tags=["classrooms"])

def get_classroom_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> ClassroomService:
    """Dependency to provide ClassroomService"""
    return ClassroomService(db)

@router.post("/", response_model=Classroom)
async def create_classroom(
    data: ClassroomCreate,
    service: ClassroomService = Depends(get_classroom_service),
    user: str = Depends(check_admin_role),
):
    """Create a new classroom"""
    return await service.create_classroom(data, user.identification_number)

@router.get("/{classroom_id}", response_model=Classroom)
async def get_classroom(
    classroom_id: str = Path(..., title="The ID of the classroom to get"),
    service: ClassroomService = Depends(get_classroom_service),
    user: str = Depends(check_admin_role),
):
    """Get a specific classroom by ID"""
    return await service.get_by_id_or_raise(classroom_id, "Classroom")

@router.get("/", response_model=List[Classroom])
async def list_classrooms(
    skip: int = 0,
    limit: int = 100,
    service: ClassroomService = Depends(get_classroom_service),
    user: str = Depends(check_teacher_role),
):
    """List all classrooms with pagination"""
    return await service.get_all(skip, limit)

@router.put("/{classroom_id}", response_model=Classroom)
async def update_classroom(
    data: ClassroomUpdate,
    classroom_id: str = Path(..., title="The ID of the classroom to update"),
    service: ClassroomService = Depends(get_classroom_service),
    user: str = Depends(check_admin_role),
):
    """Update a specific classroom"""
    return await service.update_classroom(classroom_id, data, user.identification_number)

@router.delete("/{classroom_id}")
async def delete_classroom(
    classroom_id: str = Path(..., title="The ID of the classroom to delete"),
    service: ClassroomService = Depends(get_classroom_service),
    user: str = Depends(check_admin_role),
):
    """Soft delete a classroom"""
    success = await service.delete_classroom(classroom_id, user)
    if not success:
        raise NotFoundException("Classroom", classroom_id)
    return {"message": "Classroom is disabled"}
