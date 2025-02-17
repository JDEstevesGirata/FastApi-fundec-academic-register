"""Help to authenticate"""

from datetime import datetime, timedelta
from fastapi import HTTPException, Request
from passlib.context import CryptContext
import jwt
from app.exceptions.http_exceptions import UnauthorizedException
from app.settings.settings import settings
from app.utils.constants import ADMIN, TEACHER

# Fetch values from the settings
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Initialize password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Generates a hashed password using bcrypt.

    :param password: Plain text password.
    :return: Hashed password.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies if the given password matches the stored hash.

    :param plain_password: Plain text password.
    :param hashed_password: Hashed password.
    :return: True if passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Generates a JWT access token with expiration.

    :param data: Payload data to encode.
    :param expires_delta: Expiration time for the token.
    :return: Encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    """
    Decodes a JWT access token and returns the payload.

    :param token: Encoded JWT token.
    :return: Decoded payload data.
    :raises UnauthorizedException: If token is expired or invalid.
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise UnauthorizedException("Token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise UnauthorizedException("Invalid token") from exc

async def check_admin_role(request: Request) -> dict:
    """
    Verify if the user has administrator role.
    The user is retrieved from the request state.

    :param request: The HTTP request, where the user object is stored in state.
    :return: User object if authorized
    :raises HTTPException: If user doesn't have admin role
    """
    user = request.state.user
    if user.role != ADMIN:
        raise HTTPException(
            status_code=403,
            detail="You don't have sufficient privileges"
        )
    return user

async def check_teacher_role(request: Request) -> dict:
    """
    Verify if the user has administrator or teacher role.
    The user is retrieved from the request state.

    :param request: The HTTP request, where the user object is stored in state.
    :return: User object if authorized
    :raises HTTPException: If user doesn't have admin or teacher role
    """
    user = request.state.user
    if user.role != ADMIN or TEACHER:
        raise HTTPException(
            status_code=403,
            detail="You don't have sufficient privileges"
        )
    return user
