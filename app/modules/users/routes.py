"""User routes"""

from datetime import timedelta
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.dependencies import get_database
from app.modules.users.models import LoginRequest, UserCreate
from app.modules.users.service import UserService
from app.utils.security import create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_user_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> UserService:
    """Dependency to provide ClassroomService"""
    return UserService(db)

@router.post("/register")
async def register_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """
    Endpoint para crear un nuevo usuario.

    :param user_data: Datos necesarios para la creación del usuario.
    :param user_service: Dependencia de UserService para acceder a la lógica de creación.
    :return: Mensaje de éxito con los detalles del nuevo usuario.
    """
    user = await user_service.create_user(user_data)
    return {"message": "User created successfully", "user": user}

@router.post("/login")
async def login(
    request: LoginRequest,
    user_service: UserService = Depends(get_user_service)):
    """
    Login endpoint for users to authenticate with their credentials.

    :param identification_number: User's identification number.
    :param password: User's password.
    :param db: Database dependency.
    :return: JWT access token upon successful login.
    """
    identification_number = request.identification_number
    password = request.password
    user = await user_service.authenticate_user(identification_number, password)

    token_data = {
        "sub": str(user["_id"]),
        "name": user["name"],
        "lastname": user["lastname"],
        "identification_number": user["identification_number"],
        "role": user["role"],
        "email": user["email"],
    }

    # Crear el token
    token = create_access_token(token_data, timedelta(hours=2))
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends()):
    """
    Retrieve the current authenticated user's information.

    :param token: JWT token.
    :param db: Database dependency.
    :return: User data.
    """
    payload = decode_access_token(token)
    user = await UserService(db).get_by_id(payload["sub"])
    return user
