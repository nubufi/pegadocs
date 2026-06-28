from unittest.mock import Mock
from app.presentation.controllers.database_controller import DataBaseController
from app.application.services.database_service import DatabaseService
from app.presentation.schemas.database_schemas import (
    CreateDataBaseIndexRequest,
    CreateDataBaseIndexResponse,
    ListDataBaseIndexResponse,
)


class TestDataBaseController:
    """Unit tests for DataBaseController"""

    def setup_method(self):
        self.mock_db_service = Mock(spec=DatabaseService)
        self.db_controller = DataBaseController(self.mock_db_service)

    def test_create_database_index_success(self):
        """Test successful database index creation"""
        request = CreateDataBaseIndexRequest(
            name="Test DB",
            type="postgres",
            config={"host": "localhost"},
            storage_type="vector",
        )
        user_id = "user123"
        self.mock_db_service.create_database_index.return_value = "db123"

        result = self.db_controller.create_database_index(request, user_id)

        assert isinstance(result, CreateDataBaseIndexResponse)
        assert result.id == "db123"
        self.mock_db_service.create_database_index.assert_called_once_with(
            user_id=user_id,
            db_name="Test DB",
            db_type="postgres",
            storage_type="vector",
            config={"host": "localhost"},
        )

    def test_list_database_indexes_success(self):
        """Test successful listing of database indexes"""
        user_id = "user123"
        self.mock_db_service.list_database_indexes.return_value = [
            {
                "id": "db1",
                "name": "DB 1",
                "type": "postgres",
                "config": {},
                "storage_type": "vector",
                "created_at": "2025-07-24T12:00:00Z",
                "is_default": True,
            }
        ]

        result = self.db_controller.list_database_indexes(user_id)

        assert isinstance(result, list)
        assert isinstance(result[0], ListDataBaseIndexResponse)
        assert result[0].id == "db1"
        assert result[0].is_default is True
        assert result[0].created_at == "2025-07-24T12:00:00Z"

    def test_delete_database_index_success(self):
        """Test successful deletion of database index"""
        db_id = "db1"
        user_id = "user123"
        result = self.db_controller.delete_database_index(db_id, user_id)

        assert result == {"message": "Database index deleted successfully"}
        self.mock_db_service.delete_database_index.assert_called_once_with(
            db_id, user_id
        )
