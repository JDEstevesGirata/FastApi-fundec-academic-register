"""Main function"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.dependencies import get_database
from app.db.mongodb import MongoDB
from app.middlewares.auth_middleware import JWTAuthMiddleware
from app.middlewares.error_handler import error_handler_middleware
from app.modules.users.routes import router as auth_router
from app.modules.classrooms.routes import router as classroom_router
from app.modules.teachers.routes import teacher_router
from app.modules.courses.routes import course_router

@asynccontextmanager
async def lifespan(_app: FastAPI):  # Cambié 'app' por '_app' para evitar redefinición
    """Handles the startup and shutdown events"""
    await MongoDB.connect()  # Initialize MongoDB connection
    yield
    await MongoDB.close()  # Close MongoDB connection on shutdown

# Initialize FastAPI app
app = FastAPI(  # Cambié 'app' por 'api_app'
    title="Mi API",
    description="API con MongoDB",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Permite solicitudes solo desde este origen
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)

# Registro de middlewares
app.middleware("http")(error_handler_middleware)

# Add JWT authentication middleware with dependency injection
app.add_middleware(
    JWTAuthMiddleware,
    db_dependency=get_database,
    exclude_paths={
        "/auth/login",
        "/auth/register",
        "/docs",
        "/redoc",
        "/openapi.json"
    }
)

# Registro de rutas
app.include_router(auth_router)
app.include_router(classroom_router)
app.include_router(teacher_router)
app.include_router(course_router)
