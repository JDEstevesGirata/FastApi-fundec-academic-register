"""Dependencies"""
from fastapi import HTTPException
from motor import motor_asyncio
from app.db.mongodb import MongoDB

async def get_database() -> motor_asyncio.AsyncIOMotorDatabase:
    """
    Dependency para inyectar la base de datos en los endpoints.
    Lanza un error 500 si la base de datos no está conectada.
    """
    if MongoDB.db is None:
        raise HTTPException(status_code=500, detail="MongoDB connection is not initialized")
    return MongoDB.db
