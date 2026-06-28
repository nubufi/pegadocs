from typing import Any, Dict, List
import uuid

from loguru import logger

from app.application.exceptions import (
    CollectionCreationException,
    CollectionDeletionException,
    CollectionListException,
)
from app.application.protocols.vector_store_protocol import VectorStoreProtocol
from app.application.services.chat_service import ChatService
from app.application.services.data_source_service import DataSourceService
from app.infra.config import settings
from app.infra.utils.supabase_utils import add_item, fetch_items


class CollectionService:
    """Business logic for vector store operations"""

    def __init__(
        self,
        vector_store: VectorStoreProtocol,
        data_source_service: DataSourceService,
        chat_service: ChatService,
    ) -> None:
        self.vector_store = vector_store
        self.data_source_service = data_source_service
        self.chat_service = chat_service

    def delete_collection(self, user_id: str) -> None:
        logger.info(f"Deleting collection '{self.vector_store.collection_id}'")
        try:
            self.vector_store.delete_collection()
        except Exception as e:
            logger.exception("Vector store collection deletion failed.")

        try:
            self.data_source_service.delete_data_sources_by_collection(
                self.vector_store.collection_id, user_id
            )
        except Exception as e:
            raise CollectionDeletionException(f"Failed to delete collection: {str(e)}")

        try:
            self.chat_service.delete_chats_by_collection(
                self.vector_store.collection_id, user_id
            )
        except Exception as e:
            raise CollectionDeletionException(f"Failed to delete collection: {str(e)}")

        logger.debug(
            f"Collection '{self.vector_store.collection_id}' deleted successfully."
        )

    def list_collections(self, user_id: str) -> List[Dict[str, Any]]:
        logger.info(f"Listing collections for user_id={user_id}")
        try:
            collections = fetch_items(
                settings.COLLECTIONS_TABLE_NAME, "user_id", user_id
            )
            logger.debug(f"{len(collections)} collections found for user_id={user_id}")
            return collections
        except Exception as e:
            logger.exception("Collection listing failed.")
            raise CollectionListException(f"Failed to list collections: {str(e)}")

    def create_collection(
        self,
        collection_name: str,
        database_id: str,
        user_id: str,
        embedding_model_id: str,
    ) -> str | None:
        logger.info(
            f"Creating collection '{collection_name}' for user_id={user_id}, db_id={database_id}, embedding_model_id={embedding_model_id}"
        )
        try:
            collection_id = str(uuid.uuid4()).replace("-", "")
            add_item(
                settings.COLLECTIONS_TABLE_NAME,
                {
                    "name": collection_name,
                    "database_id": database_id,
                    "user_id": user_id,
                    "embedding_model_id": embedding_model_id,
                    "id": collection_id,
                },
            )
            logger.debug(
                f"Collection '{collection_name}' created successfully with ID: {collection_id}"
            )
            return collection_id
        except Exception as e:
            logger.exception("Collection creation failed.")
            raise CollectionCreationException(f"Failed to create collection: {str(e)}")
