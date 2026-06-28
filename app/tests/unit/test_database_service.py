from unittest.mock import MagicMock, patch

import pytest

from app.application.exceptions import (
    DatabaseIndexCreationException,
    DatabaseIndexDeletionException,
    DatabaseIndexListException,
    OperationFailedException,
)
from app.application.services.database_service import DatabaseService


class TestDatabaseService:
    def setup_method(self):
        self.service = DatabaseService()
        self.user_id = "test-user"
        self.db_name = "TestDB"
        self.db_type = "postgres"
        self.config = {"host": "localhost", "port": 5432}
        self.table_name = "databases_test"

    @patch("app.application.services.database_service.fetch_items")
    def test_get_default_database_index_success(self, mock_supabase):
        mock_supabase.return_value = [{"id": "default-id", "is_default": True}]

        result = self.service.get_default_database_indexes()
        assert result == [{"id": "default-id", "is_default": True, "config": {}}]

    @patch("app.application.services.database_service.fetch_items")
    def test_get_default_database_index_failure(self, mock_supabase):
        mock_supabase.side_effect = Exception("query failed")

        with pytest.raises(
            OperationFailedException,
            match="Failed to get default database index: query failed",
        ):
            self.service.get_default_database_indexes()

    @patch(
        "app.application.services.database_service.encrypt_dict",
        return_value={"encrypted": "config"},
    )
    @patch("app.application.services.database_service.add_item")
    def test_create_database_index_success(self, mock_supabase, mock_encrypt):
        mock_supabase.return_value = MagicMock(data=[{"id": "new-db-id"}])

        result = self.service.create_database_index(
            self.user_id, self.db_name, self.db_type, self.config, "vector"
        )
        assert result == "new-db-id"

    @patch(
        "app.application.services.database_service.encrypt_dict",
        return_value={"encrypted": "config"},
    )
    @patch("app.application.services.database_service.add_item")
    def test_create_database_index_failure(self, mock_supabase, mock_encrypt):
        mock_supabase.side_effect = Exception("insert error")

        with pytest.raises(
            DatabaseIndexCreationException,
            match="Failed to generate database index: insert error",
        ):
            self.service.create_database_index(
                self.user_id, self.db_name, self.db_type, self.config, "vector"
            )

    @patch.object(
        DatabaseService,
        "get_default_database_indexes",
        return_value=[{"id": "default-id", "is_default": True}],
    )
    @patch("app.application.services.database_service.fetch_items")
    def test_list_database_indexes_success(self, mock_supabase, mock_default_index):
        mock_supabase.return_value = [{"id": "user-db-id", "user_id": self.user_id}]
        result = self.service.list_database_indexes(self.user_id)
        assert result == [
            {"id": "default-id", "is_default": True},
            {"id": "user-db-id", "user_id": self.user_id},
        ]

    @patch.object(DatabaseService, "get_default_database_indexes", return_value={})
    @patch("app.application.services.database_service.fetch_items")
    def test_list_database_indexes_failure(self, mock_supabase, mock_default_index):
        mock_supabase.side_effect = Exception("fetch failed")

        with pytest.raises(
            DatabaseIndexListException,
            match="Failed to list database indexes: fetch failed",
        ):
            self.service.list_database_indexes(self.user_id)

    @patch("app.application.services.database_service.delete_item")
    def test_delete_database_index_success(self, mock_supabase):
        mock_supabase.return_value = MagicMock(data=[{"id": "deleted-id"}])
        self.service.delete_database_index("deleted-id", "user-id")

    @patch("app.application.services.database_service.delete_item")
    def test_delete_database_index_failure(self, mock_supabase):
        mock_supabase.side_effect = Exception("delete failure")

        with pytest.raises(
            DatabaseIndexDeletionException,
            match="Failed to delete database index: delete failure",
        ):
            self.service.delete_database_index("some-id", "user-id")
