from pydantic import BaseModel, Field
from app.models.base_model import MongoBaseModel, AuditFields
from app.utils.mongo import convert_object_id

class FormRegisterBase(BaseModel):
    """Base fields for FormRegister"""
    dia: str = Field(..., min_length=1)
    fecha: str = Field(..., min_length=1)
    jornada: str
    aula: str = Field(..., min_length=1)
    nombre: str = Field(..., min_length=1)
    apellido: str = Field(..., min_length=1)
    cedula: str = Field(..., min_length=5, max_length=20)
    modulo: str = Field(..., min_length=1)
    contenido: str = Field(..., min_length=1)
    horaEntrada: str = Field(..., min_length=1)
    horaSalida: str = Field(..., min_length=1)
    cantidadHoras: float
    horaRegistroEntrada: str | None
    direccion: str | None

class FormRegister(FormRegisterBase, MongoBaseModel, AuditFields):
    """Complete FormRegister model"""

class FormRegisterCreate(FormRegisterBase):
    """Schema for creating a FormRegister entry"""

class FormRegisterUpdate(FormRegisterBase):
    """Schema for updating a FormRegister entry"""
    dia: str | None = None
    fecha: str | None = None
    jornada: str | None = None
    aula: str | None = None
    nombre: str | None = None
    apellido: str | None = None
    cedula: str | None = None
    modulo: str | None = None
    contenido: str | None = None
    horaEntrada: str | None = None
    horaSalida: str | None = None
    cantidadHoras: str | None = None
    registroSalida: bool | None = None
    horaRegistroEntrada: str | None = None
    direccion: str | None = None

class FormRegisterResponse(FormRegisterBase):
    """Response model for FormRegister with string _id"""
    id: str = Field(alias="_id")

    @classmethod
    def from_mongo(cls, data: dict):
        """Convert ObjectId to string in the response"""
        return cls(**convert_object_id(data))
