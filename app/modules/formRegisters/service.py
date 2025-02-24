"""
Service CRUD Class Register
"""

from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.modules.formRegisters.models import FormRegister, FormRegisterCreate, FormRegisterUpdate
from app.utils.crud_base import CRUDBase


class FormRegisterService(CRUDBase[FormRegister]):
    """Service layer for handling FormRegister-related operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize FormRegisterService with database connection."""
        super().__init__(db, "form_registers", FormRegister)

    async def create_form_register(self, data: FormRegisterCreate, created_by: str) -> FormRegister:
        """Create a new FormRegister entry."""
        return await self.create(data.model_dump(), created_by)

    async def get_all_form_registers(self, skip: int = 0, limit: int = 100) -> List[FormRegister]:
        """Retrieve all form registers with pagination."""
        return [
            FormRegister(**form_register) for form_register in await super().get_all(skip, limit)]

    async def update_form_register(self, form_register_id: str, data: FormRegisterUpdate, updated_by: str) -> FormRegister:
        """Update form register details."""
        return await self.update(form_register_id, data.model_dump(exclude_unset=True), updated_by)

    async def delete_form_register(self, form_register_id: str, deleted_by: str) -> bool:
        """Disable a form register instead of deleting it permanently."""
        await self.get_by_id_or_raise(form_register_id, "FormRegister")
        return await super().delete(form_register_id, deleted_by)

    async def get_teacher_forms(self, teacher_identification_number: str, skip: int = 0, limit: int = 100) -> List[FormRegister]:
        """Retrieve all forms for a specific teacher."""

        query = {"cedula": teacher_identification_number}
        forms = await self.collection.find(query).skip(skip).limit(limit).to_list(length=limit)

        return [FormRegister(**self._convert_document(form)) for form in forms]

    def _convert_document(self, doc):
        """Convert MongoDB document to Python dictionary and handle ObjectId"""
        doc["_id"] = str(doc["_id"]) if "_id" in doc else None
        return doc