"""
Base CRUD class for handling common database operations.
"""

from typing import Generic, TypeVar, List, Optional, Type
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.exceptions.http_exceptions import NotFoundException

T = TypeVar("T", bound=BaseModel)  # Modelo de datos basado en Pydantic

class CRUDBase(Generic[T]):
    """Generic CRUD operations for MongoDB collections."""

    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str, model: Type[T]):
        """
        Initialize CRUDBase with a MongoDB collection.

        :param db: AsyncIOMotorDatabase instance.
        :param collection_name: Name of the MongoDB collection.
        :param model: Pydantic model associated with the collection.
        """
        self.db = db
        self.collection = db[collection_name]
        self.model = model  # Modelo Pydantic para conversión

    async def create(self, data: dict, created_by: str) -> T:
        """
        Insert a new document into the collection.

        :param data: Dictionary representing the document.
        :param created_by: User who created the document.
        :return: Created document with ID.
        """
        data.update({"created_by": created_by, "is_active": True})
        result = await self.collection.insert_one(data)
        return await self.get_by_id(result.inserted_id)

    async def get_by_id(self, document_id: str) -> Optional[T]:
        """
        Retrieve a document by its ID.

        :param document_id: The document ID.
        :return: The document or None if not found.
        """
        object_id = self._get_valid_object_id(document_id)
        if not object_id:
            return None

        document = await self.collection.find_one({"_id": object_id, "is_active": True})
        return self._convert_document(document)

    async def get_by_id_or_raise(self, document_id: str, resource_name: str) -> T:
        """
        Retrieve a document by ID or raise a NotFoundException.

        :param document_id: The document ID.
        :param resource_name: The name of the resource (for error messages).
        :return: The document if found.
        :raises NotFoundException: If the document does not exist.
        """
        document = await self.get_by_id(document_id)
        if not document:
            raise NotFoundException(resource_name, document_id)
        return document

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """
        Retrieve all active documents with pagination.

        :param skip: Number of documents to skip.
        :param limit: Maximum number of documents to return.
        :return: List of documents.
        """
        cursor = self.collection.find({"is_active": True}).skip(skip).limit(limit)
        return [self._convert_document(doc) async for doc in cursor]

    async def update(self, document_id: str, data: dict, updated_by: str) -> Optional[T]:
        """
        Update an existing document.

        :param document_id: The document ID.
        :param data: Dictionary with updated fields.
        :param updated_by: User who is updating the document.
        :return: The updated document or None if not found.
        """
        object_id = self._get_valid_object_id(document_id)
        if not object_id:
            return None

        data["updated_by"] = updated_by
        update_result = await self.collection.update_one(
            {"_id": object_id, "is_active": True},
            {"$set": data}
        )
        if update_result.matched_count == 0:
            return None

        return await self.get_by_id(document_id)

    async def delete(self, document_id: str, deleted_by: str) -> bool:
        """
        Soft delete a document by setting 'is_active' to False.

        :param document_id: The document ID.
        :param deleted_by: User performing the deletion.
        :return: True if deletion was successful, False otherwise.
        """
        object_id = self._get_valid_object_id(document_id)
        if not object_id:
            return False

        delete_result = await self.collection.update_one(
            {"_id": object_id, "is_active": True},
            {"$set": {"is_active": False, "deleted_by": deleted_by}}
        )
        return delete_result.matched_count > 0

    def _get_valid_object_id(self, document_id: str) -> Optional[ObjectId]:
        """
        Validate and convert a string ID to ObjectId.

        :param document_id: The string ID to validate.
        :return: ObjectId if valid, otherwise None.
        """
        return ObjectId(document_id) if ObjectId.is_valid(document_id) else None

    def _convert_document(self, document: Optional[dict]) -> Optional[T]:
        """
        Convert a MongoDB document to a Pydantic model.

        :param document: The document to convert.
        :return: A Pydantic model or None if document is None.
        """
        if not document:
            return None
        document["_id"] = str(document["_id"])  # Convert ObjectId to string
        return self.model(**document)
