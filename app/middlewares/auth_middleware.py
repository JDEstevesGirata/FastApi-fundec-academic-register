"""
JWT authentication middleware for FastAPI applications.
Handles token verification and user authentication using dependency injection.
"""

import logging
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.modules.users.service import UserService
from app.utils.security import decode_access_token
from app.db.dependencies import get_database

logger = logging.getLogger(__name__)

class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce authentication on protected routes.
    Uses FastAPI dependency injection for database access.
    """

    def __init__(
        self,
        app,
        db_dependency: Callable[[], AsyncIOMotorDatabase] = get_database,
        exclude_paths: set[str] = None
    ):
        """
        Initialize the middleware with database dependency and optional path exclusions.
        
        :param app: The FastAPI application
        :param db_dependency: Callable that returns database connection
        :param exclude_paths: Set of paths to exclude from authentication
        """
        super().__init__(app)
        self.security = HTTPBearer()
        self.db_dependency = db_dependency
        self.exclude_paths = exclude_paths or {
            "/auth/login",
            "/auth/register",
            "/docs",
            "/redoc",
            "/openapi.json"
        }

    async def dispatch(self, request: Request, call_next):
        """
        Process each request through the middleware.
        
        :param request: The incoming request
        :param call_next: The next middleware/route handler
        :return: The response
        """
        # Check if the path should be excluded from authentication
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        try:
            # Get token from header
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                raise HTTPException(status_code=403, detail="No authorization header")

            # Validate token format
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=403,
                    detail="Invalid authentication scheme"
                )

            try:
                # Decode and validate token
                payload = decode_access_token(token)
            except Exception as exc:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired token"
                ) from exc

            # Get database connection using dependency
            db = await self.db_dependency()
            # Get user from database
            user_service = UserService(db)
            user = await user_service.get_by_id(payload["sub"])
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="User not found"
                )
            if not user.is_active:
                raise HTTPException(
                    status_code=401,
                    detail="User is inactive"
                )

            # Add user to request state
            request.state.user = user
            # Continue with the request
            response = await call_next(request)
            return response

        except HTTPException as exc:
            raise exc
        except Exception as exc:
            logger.error("Unexpected error in JWT middleware: %s", exc, exc_info=True)

            raise HTTPException(
                status_code=500,
                detail="Internal server error"
            ) from exc
