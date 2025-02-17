from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.exceptions.http_exceptions import DuplicateResourceException
from app.modules.form_registers.models import FormRegister, FormRegisterCreate, FormRegisterUpdate
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
        return [FormRegister(**form_register) for form_register in await super().get_all(skip, limit)]

    async def update_form_register(self, form_register_id: str, data: FormRegisterUpdate, updated_by: str) -> FormRegister:
        """Update form register details."""
        form_register = await self.get_by_id_or_raise(form_register_id, "FormRegister")
        return await self.update(form_register_id, data.model_dump(exclude_unset=True), updated_by)

    async def delete_form_register(self, form_register_id: str, deleted_by: str) -> bool:
        """Disable a form register instead of deleting it permanently."""
        await self.get_by_id_or_raise(form_register_id, "FormRegister")
        return await super().delete(form_register_id, deleted_by)
    
    async def get_teacher_forms(self, teacher_identification_number: str, skip: int = 0, limit: int = 100) -> List[FormRegister]:
        """Retrieve all forms for a specific teacher."""
        query = {"cedula": teacher_identification_number}  # Filtrar por identificación
        forms = await self.collection.find(query).skip(skip).limit(limit).to_list(length=limit)
        return [FormRegister(**form) for form in forms]

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[FormRegister]:
        """Retrieve all forms."""
        forms = await self.collection.find({}).skip(skip).limit(limit).to_list(length=limit)
        return [FormRegister(**form) for form in forms]

    async def delete_form(self, form_id: str, deleted_by: str) -> bool:
        """Disable a form instead of deleting it permanently."""
        form = await self.get_by_id_or_raise(form_id)
        return await self.collection.update_one({"_id": form["_id"]}, {"$set": {"is_active": False}})
