""" Service CRUD Teachers """

from typing import List
from bson import ObjectId
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.exceptions.http_exceptions import DuplicateResourceException
from app.modules.teachers.models import Teacher, TeacherCreate, TeacherUpdate
from app.utils.crud_base import CRUDBase

class TeacherService(CRUDBase[Teacher]):
    """Service layer for handling Teacher-related operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize TeacherService with database connection."""
        super().__init__(db, "teachers", Teacher)

    async def create_teacher(self, data: TeacherCreate, created_by: str) -> Teacher:
        """Create a new teacher after checking for duplicate email."""
        await self._check_duplicate_identification_number(data.identification_number)
        await self._check_duplicate_email(data.email)
        return await self.create(data.model_dump(), created_by)

    async def get_all_teachers(self, skip: int = 0, limit: int = 100) -> List[Teacher]:
        """Retrieve all teachers with pagination."""
        return [Teacher(**teacher) for teacher in await super().get_all(skip, limit)]

    async def update_teacher(self, teacher_id: str, data: TeacherUpdate, updated_by: str) -> Teacher:
        """Update teacher details after checking for duplicate email and identification number."""

        try:
            obj_id = ObjectId(teacher_id)
        except Exception as exc:
            raise HTTPException(status_code=400, detail="Invalid teacher ID format") from exc

        teacher = await self.get_by_id_or_raise(teacher_id, "Teacher")

        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")

        if data.email and data.email != teacher.email:
            await self._check_duplicate_email(data.email, exclude_id=teacher.id)

        if data.identification_number and data.identification_number != teacher.identification_number:
            await self._check_duplicate_identification_number(data.identification_number, exclude_id=teacher.id)

        await self.update(obj_id, data.model_dump(exclude_unset=True), updated_by)

        return await self.get_by_id_or_raise(teacher_id, "Teacher")


    async def delete_teacher(self, teacher_id: str, deleted_by: str) -> bool:
        """Disable a teacher instead of deleting them permanently."""
        await self.get_by_id_or_raise(teacher_id, "Teacher")
        return await super().delete(teacher_id, deleted_by)

    async def _check_duplicate_email(self, email: str, exclude_id: str = None) -> None:
        """Check if a teacher with the given email already exists."""
        query = {"email": email, "is_active": True}
        if exclude_id:
            query["_id"] = {"$ne": exclude_id}
        if await self.collection.find_one(query):
            raise DuplicateResourceException("Teacher", "email", email)

    async def _check_duplicate_identification_number(
            self, identification_number: str, exclude_id: str = None) -> None:
        """Check if a teacher with the given identification number already exists."""
        query = {"identification_number": identification_number, "is_active": True}
        if exclude_id:
            query["_id"] = {"$ne": exclude_id}
        if await self.collection.find_one(query):
            raise DuplicateResourceException(
                "Teacher", "identification_number", identification_number)
        