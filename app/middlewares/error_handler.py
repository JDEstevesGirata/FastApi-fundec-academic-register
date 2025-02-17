"""
Global error handler middleware to catch and format all exceptions
in a consistent way across the application.
"""

import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from app.exceptions.http_exceptions import BaseAPIException

# Configuración de logging
logger = logging.getLogger(__name__)

async def error_handler_middleware(request: Request, call_next):
    """
    Middleware to handle exceptions and return standardized JSON responses.
    """
    try:
        return await call_next(request)
    except BaseAPIException as exc:
        # Manejo de excepciones personalizadas
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail
        )

    except HTTPException as exc:
        # Manejo de HTTPException (errores nativos de FastAPI)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": exc.detail,
                "error_code": "HTTP_EXCEPTION",
                "details": {"method": request.method, "url": str(request.url)}
            }
        )

    except (ValueError, TypeError, KeyError) as exc:
        # Captura de excepciones específicas de Python
        logger.warning("Application error: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "Invalid input",
                "error_code": "BAD_REQUEST",
                "details": {"error": str(exc), "method": request.method, "url": str(request.url)}
            }
        )

    except Exception as exc:  # noqa: BLE001
        # Captura de errores inesperados con logging seguro
        logger.error("Unhandled exception: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "Internal server error",
                "error_code": "INTERNAL_SERVER_ERROR",
                "details": {"method": request.method, "url": str(request.url)}
            }
        )
