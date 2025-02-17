"""
Service CRUD Classroom
"""

from typing import List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.exceptions.http_exceptions import DuplicateResourceException
from app.modules.classrooms.models import Classroom, ClassroomCreate, ClassroomUpdate
from app.utils.crud_base import CRUDBase

class ClassroomService(CRUDBase[Classroom]):
    """Service layer for handling Classroom-related operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize the service with the 'classrooms' collection."""
        super().__init__(db, "classrooms", Classroom)

    async def create_classroom(self, data: ClassroomCreate, created_by: str) -> Classroom:
        """Create a new classroom with duplicate code validation."""
        await self._check_duplicate_code(data.code)
        return await self.create(data.model_dump(), created_by)

    async def get_all_classrooms(self, skip: int = 0, limit: int = 100) -> List[Classroom]:
        """Retrieve a list of all classrooms with pagination."""
        return [Classroom(**classroom) for classroom in await super().get_all(skip, limit)]

    async def update_classroom(
            self, classroom_id: str, data: ClassroomUpdate, updated_by: str) -> Classroom:
        """Update a classroom with duplicate code validation."""
        classroom = await self.get_by_id_or_raise(classroom_id, "Classroom")

        if data.code and data.code != classroom.code:
            await self._check_duplicate_code(data.code, exclude_id=classroom.id)

        return await self.update(classroom_id, data.model_dump(exclude_unset=True), updated_by)

    async def delete_classroom(self, classroom_id: str, deleted_by: str) -> bool:
        """Soft delete (disable) a classroom by setting `is_active` to False."""
        await self.get_by_id_or_raise(classroom_id, "Classroom")
        return await super().delete(classroom_id, deleted_by)

    async def _check_duplicate_code(self, code: str, exclude_id: ObjectId = None) -> None:
        """Check if a classroom with the given code already exists."""
        query = {"code": code, "is_active": True}
        if exclude_id:
            query["_id"] = {"$ne": exclude_id}

        if await self.collection.find_one(query):
            raise DuplicateResourceException("Classroom", "code", code)
