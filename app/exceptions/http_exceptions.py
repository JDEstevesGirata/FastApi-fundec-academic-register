"""
Custom HTTP exceptions for better error handling and consistent
error responses across the application.
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException

class BaseAPIException(HTTPException):
    """Base API Exception that extends FastAPI's HTTPException"""
    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail={
            "message": message,
            "error_code": error_code,
            "details": details or {}
        })

class NotFoundException(BaseAPIException):
    """Exception for resource not found errors"""
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            status_code=404,
            message=f"{resource} with id {resource_id} not found",
            error_code="RESOURCE_NOT_FOUND",
            details={"resource": resource, "id": resource_id}
        )

class DuplicateResourceException(BaseAPIException):
    """Exception for duplicate resource errors"""
    def __init__(self, resource: str, field: str, value: str):
        super().__init__(
            status_code=409,
            message=f"{resource} with {field} {value} already exists",
            error_code="DUPLICATE_RESOURCE",
            details={"resource": resource, "field": field, "value": value}
        )
