from typing import Any, Dict, List

from app.application.services.collection_service import CollectionService
from app.presentation.schemas.collection_schemas import (
    CreateCollectionRequest,
    CreateCollectionResponse,
)


class CollectionController:
    """Controller for vector store operations"""

    def __init__(self, collection_service: CollectionService):
        self.collection_service = collection_service

    def delete_collection(self, user_id: str) -> Dict[str, str]:
        """
        Handle delete collection request

        Args:
            user_id (str): The ID of the user requesting the deletion
        Returns:
            Dict[str, str]: A message indicating the result of the deletion
        """
        self.collection_service.delete_collection(user_id=user_id)
        collection_id = self.collection_service.vector_store.collection_id
        return {"message": f"Collection '{collection_id}' deleted successfully"}

    def list_collections(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Handle list collections request

        Args:
            user_id (str): The ID of the user whose collections to list
        Returns:
            List[Dict[str, Any]]: A list of collections associated with the user
        """
        return self.collection_service.list_collections(user_id)

    def create_collection(
        self, request: CreateCollectionRequest, user_id: str
    ) -> CreateCollectionResponse:
        """
        Handle create collection request

        Args:
            request (CreateCollectionRequest): The request containing collection details
            user_id (str): The ID of the user creating the collection
        Returns:
            CreateCollectionResponse: The response containing the created collection ID and name
        """
        collection_id = self.collection_service.create_collection(
            collection_name=request.collection_name,
            user_id=user_id,
            database_id=request.database_id,
            embedding_model_id=request.embedding_model_id,
        )
        return CreateCollectionResponse(
            collection_id=collection_id or "",
            collection_name=request.collection_name,
        )
