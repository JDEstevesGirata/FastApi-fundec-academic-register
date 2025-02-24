"""
Service CRUD Courses
"""

from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from fastapi import HTTPException

from app.exceptions.http_exceptions import DuplicateResourceException
from app.modules.courses.models import Course, CourseCreate, CourseUpdate
from app.utils.crud_base import CRUDBase


class CourseService(CRUDBase[Course]):
    """Service layer for handling Course-related operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize CourseService with database connection."""
        super().__init__(db, "courses", Course)

    async def create_course(self, data: CourseCreate, created_by: str) -> Course:
        """Create a new course after checking for duplicate code."""
        await self._check_duplicate_code(data.code)
        return await self.create(data.model_dump(), created_by)

    async def get_all_courses(self, skip: int = 0, limit: int = 100) -> List[Course]:
        """Retrieve all courses with pagination."""
        return [Course(**course) for course in await super().get_all(skip, limit)]

    async def update_course(self, course_id: str, data: CourseUpdate, updated_by: str) -> Course:
        """Update a course with duplicate code validation."""

        try:
            obj_id = ObjectId(course_id)
        except Exception as exc:
            raise HTTPException(status_code=400, detail="Invalid course ID format") from exc

        course = await self.get_by_id_or_raise(course_id, "Course")

        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        if data.code and data.code != course.code:
            await self._check_duplicate_code(data.code, exclude_id=course.id)

        await self.update(obj_id, data.model_dump(exclude_unset=True), updated_by)

        return await self.get_by_id_or_raise(course_id, "Course")

    async def delete_course(self, course_id: str, deleted_by: str) -> bool:
        """Disable a course instead of deleting it permanently."""
        await self.get_by_id_or_raise(course_id, "Course")
        return await super().delete(course_id, deleted_by)

    async def _check_duplicate_code(self, code: str, exclude_id: str = None) -> None:
        """Check if a course with the given code already exists."""
        query = {"code": code, "is_active": True}

        if exclude_id:
            query["_id"] = {"$ne": exclude_id}

        if await self.collection.find_one(query):
            raise DuplicateResourceException("Course", "code", code)
