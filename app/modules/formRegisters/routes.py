"""Form Register"""

from typing import List
from fastapi import APIRouter, Depends, Path, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.dependencies import get_database
from app.modules.formRegisters.models import FormRegister, FormRegisterCreate, FormRegisterUpdate
from app.modules.formRegisters.service import FormRegisterService
from app.utils.security import check_admin_role, check_teacher_role

form_router = APIRouter(prefix="/forms", tags=["forms"])

def get_form_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> FormRegisterService:
    """Dependency to provide FormService"""
    return FormRegisterService(db)

@form_router.post("/", response_model=FormRegister)
async def create_form(
    data: FormRegisterCreate,
    service: FormRegisterService = Depends(get_form_service),
    user: str = Depends(check_teacher_role),
):
    """Create a new form"""
    return await service.create_form(data, user.identification_number)

@form_router.get("/{form_id}", response_model=FormRegister)
async def get_form(
    form_id: str = Path(..., title="The ID of the form to get"),
    service: FormRegisterService = Depends(get_form_service),
    user: str = Depends(check_teacher_role),
):
    """Get a specific form by ID"""
    form = await service.get_by_id_or_raise(form_id)
    # Verificar si el teacher solo puede ver su formulario
    if user.role == "teacher" and form.cedula != user.identification_number:
        raise HTTPException(status_code=403, detail="Forbidden")
    return form

@form_router.get("/", response_model=List[FormRegister])
async def list_forms(
    skip: int = 0,
    limit: int = 100,
    service: FormRegisterService = Depends(get_form_service),
    user: str = Depends(check_teacher_role),  # Tanto admin como teacher pueden listar
):
    """List forms based on user role"""
    if user.role == "admin":
        return await service.get_all(skip, limit)  # Admin puede ver todos
    elif user.role == "teacher":
        return await service.get_teacher_forms(user.identification_number, skip, limit)
    else:
        raise HTTPException(status_code=403, detail="Forbidden")

@form_router.put("/{form_id}", response_model=FormRegister)
async def update_form(
    data: FormRegisterUpdate,
    form_id: str = Path(..., title="The ID of the form to update"),
    service: FormRegisterService = Depends(get_form_service),
    user: str = Depends(check_teacher_role),  # Tanto admin como teacher pueden actualizar
):
    """Update a specific form"""
    form = await service.get_by_id_or_raise(form_id)
    # Verificar si el teacher solo puede actualizar su formulario
    if user.role == "teacher" and form.cedula != user.identification_number:
        raise HTTPException(status_code=403, detail="Forbidden")
    return await service.update_form(form_id, data, user.identification_number)

@form_router.delete("/{form_id}")
async def delete_form(
    form_id: str = Path(..., title="The ID of the form to delete"),
    service: FormRegisterService = Depends(get_form_service),
    user: str = Depends(check_admin_role),  # Solo admin puede eliminar
):
    """Soft delete a form"""
    success = await service.delete_form(form_id, user)
    if not success:
        raise HTTPException(status_code=404, detail="Form not found")
    return {"message": "Form is disabled"}
