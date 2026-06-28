from unittest.mock import MagicMock, patch

import pytest

from app.application.exceptions import (
    DataSourceCreationException,
    DataSourceDeletionException,
    DataSourceListException,
    DataSourceUpdateException,
    SASUrlGenerationException,
)
from app.application.services.data_source_service import DataSourceService


class TestDataSourceService:
    def setup_method(self):
        self.service = DataSourceService()
        self.collection_id = "col-123"
        self.data_source_id = "ds-456"
        self.user_id = "user-789"
        self.ds_name = "My Drive"
        self.ds_type = "google_drive"
        self.config = {"folder": "root"}

    # ---- delete_data_source ----
    @patch("app.application.services.data_source_service.delete_item")
    @patch.object(DataSourceService, "_get_vector_store_by_collection")
    @patch.object(DataSourceService, "_get_collection_id_by_data_source")
    def test_delete_data_source_success(
        self, mock_get_collection_id, mock_get_vector_store, mock_delete_item
    ):
        mock_get_collection_id.return_value = self.collection_id
        mock_vector_store = MagicMock()
        mock_get_vector_store.return_value = mock_vector_store

        self.service.delete_data_source(self.data_source_id, self.user_id)

        mock_get_collection_id.assert_called_once_with(self.data_source_id)
        mock_get_vector_store.assert_called_once_with(self.collection_id, self.user_id)
        mock_vector_store.delete_data_source.assert_called_once_with(
            self.data_source_id
        )
        mock_delete_item.assert_called_once_with(
            self.service.table_name, "id", self.data_source_id
        )

    @patch("app.application.services.data_source_service.delete_item")
    @patch.object(DataSourceService, "_get_vector_store_by_collection")
    @patch.object(DataSourceService, "_get_collection_id_by_data_source")
    def test_delete_data_source_no_collection_skips_vector_store(
        self, mock_get_collection_id, mock_get_vector_store, mock_delete_item
    ):
        mock_get_collection_id.return_value = None

        self.service.delete_data_source(self.data_source_id, self.user_id)

        mock_get_collection_id.assert_called_once_with(self.data_source_id)
        mock_get_vector_store.assert_not_called()
        mock_delete_item.assert_called_once_with(
            self.service.table_name, "id", self.data_source_id
        )

    @patch("app.application.services.data_source_service.delete_item")
    @patch.object(DataSourceService, "_get_vector_store_by_collection")
    @patch.object(DataSourceService, "_get_collection_id_by_data_source")
    def test_delete_data_source_failure_raises_domain_exception(
        self, mock_get_collection_id, mock_get_vector_store, mock_delete_item
    ):
        mock_get_collection_id.return_value = self.collection_id
        mock_vector_store = MagicMock()
        mock_get_vector_store.return_value = mock_vector_store
        mock_delete_item.side_effect = Exception("boom")

        with pytest.raises(
            DataSourceDeletionException,
            match="Failed to delete data source: boom",
        ):
            self.service.delete_data_source(self.data_source_id, self.user_id)

        mock_get_collection_id.assert_called_once_with(self.data_source_id)
        mock_get_vector_store.assert_called_once_with(self.collection_id, self.user_id)
        mock_vector_store.delete_data_source.assert_called_once_with(
            self.data_source_id
        )
        mock_delete_item.assert_called_once_with(
            self.service.table_name, "id", self.data_source_id
        )

    def test_generate_sas_urls_success(self):
        folder_name = "ds123"
        file_paths = ["file1.txt", "folder/file2.pdf"]

        with patch(
            "app.application.services.data_source_service.generate_presigned_upload_url"
        ) as mock_generate:
            mock_generate.side_effect = lambda object_key: (
                f"https://s3.amazonaws.com/bucket/{object_key}?presigned-token",
                "application/pdf",
            )
            result = self.service.generate_sas_urls(folder_name, file_paths)

            expected = {
                "file1.txt": {
                    "url": "https://s3.amazonaws.com/bucket/ds123/file1.txt?presigned-token",
                    "content_type": "application/pdf",
                },
                "folder/file2.pdf": {
                    "url": "https://s3.amazonaws.com/bucket/ds123/folder/file2.pdf?presigned-token",
                    "content_type": "application/pdf",
                },
            }

            assert result == expected
            assert mock_generate.call_count == 2
            mock_generate.assert_any_call("ds123/file1.txt")
            mock_generate.assert_any_call("ds123/folder/file2.pdf")

    def test_generate_sas_urls_failure(self):
        folder_name = "ds123"
        file_paths = ["file1.txt"]

        with patch(
            "app.application.services.data_source_service.generate_presigned_upload_url"
        ) as mock_generate:
            mock_generate.side_effect = Exception("S3 error")

            with pytest.raises(
                SASUrlGenerationException,
                match="Failed to generate presigned URLs: S3 error",
            ):
                self.service.generate_sas_urls(folder_name, file_paths)

    # ---- add_data_source ----
    @patch(
        "app.application.services.data_source_service.encrypt_dict",
        return_value={"enc": "cfg"},
    )
    @patch("app.application.services.data_source_service.add_item")
    def test_add_data_source_success(self, mock_add_item, mock_encrypt):
        mock_add_item.return_value = MagicMock(data=[{"id": "new-ds-id"}])

        new_id = self.service.add_data_source(
            "test-user", self.collection_id, self.ds_name, self.ds_type, self.config
        )
        assert new_id == "new-ds-id"

        mock_encrypt.assert_called_once_with(self.config)
        mock_add_item.assert_called_once()
        args, kwargs = mock_add_item.call_args
        # table name
        assert args[0] == self.service.table_name
        # payload
        payload = args[1]
        assert payload["collection_id"] == self.collection_id
        assert payload["name"] == self.ds_name
        assert payload["type"] == self.ds_type
        assert payload["config"] == {"enc": "cfg"}

    @patch(
        "app.application.services.data_source_service.encrypt_dict",
        return_value={"enc": "cfg"},
    )
    @patch("app.application.services.data_source_service.add_item")
    def test_add_data_source_no_data_raises(self, mock_add_item, mock_encrypt):
        # Supabase call returns no data array
        mock_add_item.return_value = MagicMock(data=[])

        with pytest.raises(
            DataSourceCreationException, match="No data returned after creation"
        ):
            self.service.add_data_source(
                "test-user", self.collection_id, self.ds_name, self.ds_type, self.config
            )

    @patch(
        "app.application.services.data_source_service.encrypt_dict",
        return_value={"enc": "cfg"},
    )
    @patch("app.application.services.data_source_service.add_item")
    def test_add_data_source_failure(self, mock_add_item, mock_encrypt):
        mock_add_item.side_effect = Exception("insert error")

        with pytest.raises(
            DataSourceCreationException,
            match="Failed to create data source: insert error",
        ):
            self.service.add_data_source(
                "test-user", self.collection_id, self.ds_name, self.ds_type, self.config
            )

    # ---- update_data_source ----
    @patch(
        "app.application.services.data_source_service.encrypt_dict",
        return_value={"enc": "cfg"},
    )
    @patch("app.application.services.data_source_service.update_item")
    def test_update_data_source_success(self, mock_update_item, mock_encrypt):
        # should not raise
        self.service.update_data_source(
            self.user_id,
            self.data_source_id,
            self.collection_id,
            self.ds_name,
            self.ds_type,
            self.config,
        )

        mock_encrypt.assert_called_once_with(self.config)
        mock_update_item.assert_called_once_with(
            self.service.table_name,
            "id",
            self.data_source_id,
            {
                "collection_id": self.collection_id,
                "name": self.ds_name,
                "type": self.ds_type,
                "config": {"enc": "cfg"},
            },
            self.user_id,
        )

    @patch(
        "app.application.services.data_source_service.encrypt_dict",
        return_value={"enc": "cfg"},
    )
    @patch("app.application.services.data_source_service.update_item")
    def test_update_data_source_failure(self, mock_update_item, mock_encrypt):
        mock_update_item.side_effect = Exception("update blew up")

        with pytest.raises(
            DataSourceUpdateException,
            match="Failed to update data source: update blew up",
        ):
            self.service.update_data_source(
                self.user_id,
                self.data_source_id,
                self.collection_id,
                self.ds_name,
                self.ds_type,
                self.config,
            )

    # ---- list_data_sources ----
    @patch("app.application.services.data_source_service.decrypt_dict")
    @patch("app.application.services.data_source_service.fetch_items")
    def test_list_data_sources_success_with_decrypt(self, mock_fetch, mock_decrypt):
        mock_fetch.return_value = [
            {"id": "a", "collection_id": self.collection_id, "config": {"cipher": "x"}},
            {"id": "b", "collection_id": self.collection_id, "config": {"cipher": "y"}},
        ]
        # return different plaintexts per call to ensure both items are processed
        mock_decrypt.side_effect = [{"plain": "x"}, {"plain": "y"}]

        result = self.service.list_data_sources(self.collection_id)

        assert result == [
            {"id": "a", "collection_id": self.collection_id, "config": {"plain": "x"}},
            {"id": "b", "collection_id": self.collection_id, "config": {"plain": "y"}},
        ]
        mock_fetch.assert_called_once_with(
            self.service.table_name, "collection_id", self.collection_id
        )
        assert mock_decrypt.call_count == 2

    @patch("app.application.services.data_source_service.decrypt_dict")
    @patch("app.application.services.data_source_service.fetch_items")
    def test_list_data_sources_decrypt_failure_falls_back_to_empty_config(
        self, mock_fetch, mock_decrypt
    ):
        mock_fetch.return_value = [
            {"id": "a", "collection_id": self.collection_id, "config": {"cipher": "x"}},
            {"id": "b", "collection_id": self.collection_id, "config": {"cipher": "y"}},
            {"id": "c", "collection_id": self.collection_id},  # no config field
        ]
        # first decrypt ok, second raises error
        mock_decrypt.side_effect = [{"plain": "x"}, Exception("bad decrypt")]

        result = self.service.list_data_sources(self.collection_id)

        assert result[0]["config"] == {"plain": "x"}
        assert result[1]["config"] == {}  # fallback due to decrypt error
        assert "config" not in result[2] or result[2].get("config") == result[2].get(
            "config"
        )  # untouched if no config key present

    @patch("app.application.services.data_source_service.fetch_items")
    def test_list_data_sources_failure(self, mock_fetch):
        mock_fetch.side_effect = Exception("fetch failed")

        with pytest.raises(
            DataSourceListException,
            match=f"Failed to list data sources: fetch failed",
        ):
            self.service.list_data_sources(self.collection_id)
