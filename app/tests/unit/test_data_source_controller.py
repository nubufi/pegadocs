from unittest.mock import Mock

from app.application.services.data_source_service import DataSourceService
from app.presentation.controllers.data_source_controller import DataSourceController
from app.presentation.schemas.data_source_schemas import (
    CreateDataSourceRequest,
    ListDataSourcesRequest,
    SASUrlRequest,
)


class TestDataSourceController:
    """Unit tests for DataSourceController"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_data_source_service = Mock(spec=DataSourceService)
        self.mock_data_source_controller = DataSourceController(
            self.mock_data_source_service
        )

    def test_generate_sas_urls_success(self):
        # Arrange
        request = SASUrlRequest(
            folder_name="ds_123",
            file_names=["file1.pdf", "file2.pdf"],
        )

        self.mock_data_source_service.generate_sas_urls.return_value = {
            "file1.pdf": "https://s3.amazonaws.com/bucket/ds_123/file1.pdf?presigned-token",
            "file2.pdf": "https://s3.amazonaws.com/bucket/ds_123/file2.pdf?presigned-token",
        }

        # Act
        result = self.mock_data_source_controller.generate_sas_urls(request)
        # Assert
        assert "urls" in result
        assert "file1.pdf" in result["urls"]
        assert result["urls"]["file1.pdf"].startswith("https://")
        self.mock_data_source_service.generate_sas_urls.assert_called_once_with(
            folder_name="ds_123",
            file_names=["file1.pdf", "file2.pdf"],
        )

    def test_add_data_source_success(self):
        """Test successful data source addition"""
        request = CreateDataSourceRequest(
            collection_id="test-collection",
            name="Test Data Source",
            type="file",
            config={"file_path": "path/to/file.txt"},
        )

        self.mock_data_source_service.add_data_source.return_value = (
            "new-data-source-id"
        )

        result = self.mock_data_source_controller.add_data_source(request, "test-user")

        assert result.data_source_id == "new-data-source-id"
        self.mock_data_source_service.add_data_source.assert_called_once_with(
            user_id="test-user",
            collection_id="test-collection",
            data_source_name="Test Data Source",
            data_source_type="file",
            config={"file_path": "path/to/file.txt"},
        )

    def test_add_data_source_with_none_id(self):
        """Test data source addition when service returns None"""
        request = CreateDataSourceRequest(
            collection_id="test-collection",
            name="Test Data Source",
            type="file",
            config={"file_path": "path/to/file.txt"},
        )

        self.mock_data_source_service.add_data_source.return_value = None

        result = self.mock_data_source_controller.add_data_source(request, "test-user")

        assert result.data_source_id == ""

    def test_list_data_sources_success(self):
        """Test successful data source listing"""
        request = ListDataSourcesRequest(collection_id="test-collection")
        expected_data_sources = [
            {"id": "ds1", "name": "Data Source 1", "type": "file"},
            {"id": "ds2", "name": "Data Source 2", "type": "database"},
        ]

        self.mock_data_source_service.list_data_sources.return_value = (
            expected_data_sources
        )

        result = self.mock_data_source_controller.list_data_sources(request)

        assert result == expected_data_sources
        self.mock_data_source_service.list_data_sources.assert_called_once_with(
            "test-collection"
        )
