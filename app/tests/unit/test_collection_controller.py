from unittest.mock import Mock

from app.application.services.collection_service import CollectionService
from app.presentation.controllers.collection_controller import CollectionController
from app.presentation.schemas.collection_schemas import (
    CreateCollectionRequest,
)


class TestCollectionController:
    """Unit tests for CollectionController"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_collection_service = Mock(spec=CollectionService)
        self.mock_collection_service.vector_store = Mock()
        self.mock_collection_service.vector_store.collection_id = "test-collection"
        self.vector_store_controller = CollectionController(
            self.mock_collection_service
        )

    def test_delete_collection_success(self):
        """Test successful collection deletion"""
        collection_id = "test-collection"
        user_id = "test-user"

        result = self.vector_store_controller.delete_collection(user_id)

        assert result == {
            "message": "Collection 'test-collection' deleted successfully"
        }
        self.mock_collection_service.delete_collection.assert_called_once_with(user_id=user_id)

    def test_list_collections_success(self):
        """Test successful collection listing"""
        user_id = "test-user"
        expected_collections = [
            {"id": "col1", "name": "Collection 1", "user_id": user_id},
            {"id": "col2", "name": "Collection 2", "user_id": user_id},
        ]

        self.mock_collection_service.list_collections.return_value = (
            expected_collections
        )

        result = self.vector_store_controller.list_collections(user_id)

        assert result == expected_collections
        self.mock_collection_service.list_collections.assert_called_once_with(user_id)

    def test_create_collection_success(self):
        """Test successful collection creation"""
        request = CreateCollectionRequest(
            collection_name="Test Collection",
            database_id="test-db",
            embedding_model_id="test-embedding-model",
        )
        user_id = "test-user"

        self.mock_collection_service.create_collection.return_value = (
            "new-collection-id"
        )

        result = self.vector_store_controller.create_collection(request, user_id)

        assert result.collection_id == "new-collection-id"
        assert result.collection_name == "Test Collection"
        self.mock_collection_service.create_collection.assert_called_once_with(
            collection_name="Test Collection",
            database_id="test-db",
            user_id="test-user",
            embedding_model_id="test-embedding-model",
        )

    def test_create_collection_with_none_id(self):
        """Test collection creation when service returns None"""
        request = CreateCollectionRequest(
            collection_name="Test Collection",
            database_id="test-db",
            embedding_model_id="test-embedding-model",
        )
        user_id = "test-user"

        self.mock_collection_service.create_collection.return_value = None

        result = self.vector_store_controller.create_collection(request, user_id)

        assert result.collection_id == ""
        assert result.collection_name == "Test Collection"
