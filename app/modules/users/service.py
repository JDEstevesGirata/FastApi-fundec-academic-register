"""User Service"""

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.utils.crud_base import CRUDBase
from app.modules.users.models import UserCreate, UserBase
from app.exceptions.http_exceptions import UnauthorizedException
from app.utils.security import hash_password, verify_password

class UserService(CRUDBase[UserBase]):
    """
    Service class for handling user-related operations.
    Inherits from CRUDBase for basic database operations.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize the UserService with the 'users' collection.
        
        :param db: Async database instance.
        """
        super().__init__(db, "users", UserBase)

    async def create_user(self, user_data: UserCreate) -> dict:
        """
        Creates a new user with an encrypted password.

        :param user_data: User creation data.
        :return: Created user document.
        """
        user_data_dict = user_data.model_dump()
        user_data_dict["password"] = hash_password(user_data.password)  # Encrypt password
        return await self.create(user_data_dict, created_by="system")

    async def authenticate_user(self, identification_number: str, password: str) -> Optional[dict]:
        """
        Authenticates a user by verifying their password.

        :param identification_number: User's identification number.
        :param password: Raw password input.
        :return: User document if authentication is successful.
        :raises UnauthorizedException: If authentication fails.
        """
        user = await self.collection.find_one({"identification_number": identification_number})
        if not user or not verify_password(password, user["password"]):
            raise UnauthorizedException("Invalid credentials")
        return user
