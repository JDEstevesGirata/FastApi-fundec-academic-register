"""Main function"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.mongodb import MongoDB
from app.middlewares.error_handler import error_handler_middleware
from app.modules.classrooms.routes import router as classroom_router

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

# Registro de middlewares
app.middleware("http")(error_handler_middleware)

# Registro de rutas
app.include_router(classroom_router)

# @api_app.get("/ejemplo")
# async def ejemplo_endpoint(
#     db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_database)
# ):
#     """Example endpoint to test MongoDB connection"""
#     result = await db.collection.find_one({})
#     return {"mensaje": "Conexión exitosa a la base de datos", "data": result}

# @api_app.get("/ping")
# async def ping():
#     """Simple endpoint that does not interact with the database"""
#     return {"message": "Pong! The API is runningsssss"}
