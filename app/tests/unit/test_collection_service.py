from unittest.mock import Mock, patch

import pytest

from app.application.exceptions import (
    CollectionCreationException,
    CollectionListException,
)
from app.application.protocols.vector_store_protocol import VectorStoreProtocol
from app.application.services.collection_service import CollectionService


class TestCollectionService:
    """Unit tests for CollectionService"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_vector_store = Mock(spec=VectorStoreProtocol)
        self.mock_vector_store.collection_id = "col123"
        self.mock_data_source_service = Mock()
        self.mock_chat_service = Mock()
        self.collection_service = CollectionService(
            self.mock_vector_store, 
            self.mock_data_source_service, 
            self.mock_chat_service
        )

    def test_delete_collection_success(self):
        """Test successful collection deletion"""
        user_id = "test-user"

        self.collection_service.delete_collection(user_id)

        self.mock_vector_store.delete_collection.assert_called_once()
        self.mock_data_source_service.delete_data_sources_by_collection.assert_called_once_with(
            "col123", user_id
        )
        self.mock_chat_service.delete_chats_by_collection.assert_called_once_with(
            "col123", user_id
        )

    @patch("app.application.services.collection_service.fetch_items")
    def test_list_collections_success(self, mock_fetch_items):
        """Test successful collection listing"""
        user_id = "test-user"
        expected_collections = [
            {"id": "col1", "name": "Collection 1", "user_id": user_id},
            {"id": "col2", "name": "Collection 2", "user_id": user_id},
        ]

        mock_fetch_items.return_value = expected_collections

        result = self.collection_service.list_collections(user_id)

        assert result == expected_collections
        mock_fetch_items.assert_called_once()

    @patch("app.application.services.collection_service.fetch_items")
    def test_list_collections_failure(self, mock_fetch_items):
        """Test collection listing failure"""
        user_id = "test-user"

        mock_fetch_items.side_effect = Exception("Database error")

        with pytest.raises(
            CollectionListException,
            match="Failed to list collections: Database error",
        ):
            self.collection_service.list_collections(user_id)

    @patch("app.application.services.collection_service.add_item")
    def test_create_collection_success(self, mock_add_item):
        """Test successful collection creation"""
        collection_name = "Test Collection"
        user_id = "test-user"
        database_id = "test-database"
        embedding_model_id = "test-embedding-model"

        result = self.collection_service.create_collection(
            collection_name, database_id, user_id, embedding_model_id
        )

        assert result is not None
        mock_add_item.assert_called_once()

    def test_create_collection_failure(self):
        """Test collection creation failure"""
        collection_name = "Test Collection"
        user_id = "test-user"
        database_id = "test-database"
        embedding_model_id = "test-embedding-model"

    @patch("app.application.services.collection_service.add_item")
    def test_create_collection_failure(self, mock_add_item):
        """Test collection creation failure"""
        collection_name = "Test Collection"
        user_id = "test-user"
        database_id = "test-database"
        embedding_model_id = "test-embedding-model"

        mock_add_item.side_effect = Exception("Collection already exists")

        with pytest.raises(
            CollectionCreationException,
            match="Failed to create collection: Collection already exists",
        ):
            self.collection_service.create_collection(
                collection_name, database_id, user_id, embedding_model_id
            )
