"""MongoDB Connection"""
from typing import Optional
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.settings.settings import Settings


# Logger configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class MongoDB:
    """MongoDB connection handler"""
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect(cls) -> None:
        """
        Establishes a connection to MongoDB.
        Raises an exception if the connection fails.
        """
        if cls.client is None:
            settings = Settings()  # Instancia de Settings para obtener variables
            try:
                cls.client = AsyncIOMotorClient(
                    settings.MONGO_URI,
                    serverSelectionTimeoutMS=5000
                )

                # Verify connection
                await cls.client.admin.command("ping")

                # Ensure client is initialized before using it
                if cls.client is not None:
                    cls.db = cls.client.get_database(settings.MONGO_DB)
                    logger.info("Successfully connected to MongoDB")
            except Exception as e:
                logger.error("Error connecting to MongoDB: %s", e)
                raise

    @classmethod
    async def close(cls) -> None:
        """
        Closes the MongoDB connection safely.
        """
        if cls.client:
            try:
                cls.client.close()
                cls.client = None
                cls.db = None
                logger.info("MongoDB connection closed successfully")
            except Exception as e:
                logger.error("Error closing MongoDB connection: %s", e)
                raise

    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """
        Returns the database instance.
        Raises a RuntimeError if the connection is not initialized.
        """
        if cls.db is None:
            raise RuntimeError("MongoDB connection is not initialized")
        return cls.db
