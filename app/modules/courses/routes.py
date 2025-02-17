"""Courses routes"""

from typing import List
from fastapi import APIRouter, Depends, Path
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.dependencies import get_database
from app.exceptions.http_exceptions import NotFoundException
from app.modules.courses.models import Course, CourseCreate, CourseUpdate
from app.modules.courses.services import CourseService
from app.utils.security import check_admin_role

course_router = APIRouter(prefix="/courses", tags=["courses"])

def get_course_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> CourseService:
    """Dependency to provide CourseService"""
    return CourseService(db)


@course_router.post("/", response_model=Course)
async def create_course(
    data: CourseCreate,
    service: CourseService = Depends(get_course_service),
    user: str = Depends(check_admin_role),
):
    """Create a new course"""
    return await service.create_course(data, user)

@course_router.get("/{course_id}", response_model=Course)
async def get_course(
    course_id: str = Path(..., title="The ID of the course to get"),
    service: CourseService = Depends(get_course_service),
    user: str = Depends(check_admin_role),
):
    """Get a specific course by ID"""
    return await service.get_by_id_or_raise(course_id, "Course")

@course_router.get("/", response_model=List[Course])
async def list_courses(
    skip: int = 0,
    limit: int = 100,
    service: CourseService = Depends(get_course_service),
    user: str = Depends(check_admin_role),
):
    """List all courses with pagination"""
    return await service.get_all(skip, limit)

@course_router.put("/{course_id}", response_model=Course)
async def update_course(
    data: CourseUpdate,
    course_id: str = Path(..., title="The ID of the course to update"),
    service: CourseService = Depends(get_course_service),
    user: str = Depends(check_admin_role),
):
    """Update a specific course"""
    return await service.update_course(course_id, data, user)

@course_router.delete("/{course_id}")
async def delete_course(
    course_id: str = Path(..., title="The ID of the course to delete"),
    service: CourseService = Depends(get_course_service),
    user: str = Depends(check_admin_role),
):
    """Soft delete a course"""
    success = await service.delete_course(course_id, user)
    if not success:
        raise NotFoundException("Course", course_id)
    return {"message": "Course is disabled"}