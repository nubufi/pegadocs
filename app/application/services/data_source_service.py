from typing import Any, Dict, List

from loguru import logger

from app.application.exceptions import (
    DataSourceCreationException,
    DataSourceDeletionException,
    DataSourceListException,
    DataSourceUpdateException,
    SASUrlGenerationException,
)
from app.application.protocols.reader_protocol import ReaderProtocol
from app.infra.factories.reader import reader_map
from app.infra.factories.vector_store import VectorStoreFactory
from app.application.services.database_service import DatabaseService
from app.application.protocols.vector_store_protocol import VectorStoreProtocol
from app.infra.config import settings
from app.infra.utils.encrypt_utils import decrypt_dict, encrypt_dict
from app.infra.utils.s3_utils import generate_presigned_upload_url
from app.infra.utils.supabase_utils import (
    add_item,
    delete_item,
    fetch_items,
    update_item,
)


class DataSourceService:
    """Business logic for data source operations"""

    table_name = settings.DATA_SOURCES_TABLE_NAME

    def delete_data_source(self, data_source_id: str, user_id: str) -> None:
        """
        Delete a data source by its ID
        """
        logger.info(f"Attempting to delete data source with ID: {data_source_id}")
        try:
            collection_id = self._get_collection_id_by_data_source(data_source_id)
            if collection_id:
                vector_store = self._get_vector_store_by_collection(
                    collection_id, user_id
                )
                vector_store.delete_data_source(data_source_id)
        except Exception as e:
            logger.exception(
                f"Failed to delete data source from vector store {data_source_id}: {e}"
            )
        try:
            delete_item(settings.DATA_SOURCES_TABLE_NAME, "id", data_source_id)
        except Exception as e:
            logger.exception(f"Failed to delete data source {data_source_id}: {e}")
            raise DataSourceDeletionException(f"Failed to delete data source: {str(e)}")

    def add_data_source(
        self,
        user_id: str,
        collection_id: str,
        data_source_name: str,
        data_source_type: str,
        config: Dict[str, Any],
    ) -> str | None:
        """
        Add a data source to a collection
        """
        logger.info(
            f"Adding data source '{data_source_name}' of type '{data_source_type}' to collection '{collection_id}'"
        )
        try:
            reader = reader_map.get(data_source_type)
            if not reader:
                raise DataSourceCreationException(
                    f"Unsupported data source type: {data_source_type}"
                )
            reader(
                data_source_id="",
                config=config,
                chunk_size=1,
                chunk_overlap=1,
            ).validate_config(config)

            encrypted_config = encrypt_dict(config)
            logger.debug(f"Configuration encrypted for data source: {data_source_name}")
            response = add_item(
                self.table_name,
                {
                    "user_id": user_id,
                    "collection_id": collection_id,
                    "name": data_source_name,
                    "type": data_source_type,
                    "config": encrypted_config,
                },
            )

            if response and response.data:
                data_source_id = response.data[0]["id"]
                logger.debug(f"Data source added with ID: {data_source_id}")
                return data_source_id
            else:
                raise DataSourceCreationException("No data returned after creation")
        except Exception as e:
            logger.exception(f"Failed to create data source '{data_source_name}': {e}")
            raise DataSourceCreationException(f"Failed to create data source: {str(e)}")

    def update_data_source(
        self,
        user_id: str,
        data_source_id: str,
        collection_id: str,
        data_source_name: str,
        data_source_type: str,
        config: Dict[str, Any],
    ) -> None:
        """
        Update a data source's name and configuration
        """
        logger.info(f"Updating data source with ID: {data_source_id}")
        try:
            encrypted_config = encrypt_dict(config)
            logger.debug(
                f"Configuration encrypted for data source ID: {data_source_id}"
            )
            updated_data = {
                "collection_id": collection_id,
                "name": data_source_name,
                "type": data_source_type,
                "config": encrypted_config,
            }
            # Assuming update_data_source is a function similar to add_data_source
            update_item(self.table_name, "id", data_source_id, updated_data, user_id)
            logger.debug(f"Data source with ID {data_source_id} updated successfully")
        except Exception as e:
            logger.exception(f"Failed to update data source {data_source_id}: {e}")
            raise DataSourceUpdateException(f"Failed to update data source: {str(e)}")

    def list_data_sources(self, collection_id: str) -> List[Dict[str, Any]]:
        """
        List all data sources for a given collection
        """
        logger.info(f"Listing data sources for collection ID: {collection_id}")
        try:
            data_sources = fetch_items(self.table_name, "collection_id", collection_id)
            logger.debug(
                f"Retrieved {len(data_sources)} data sources for collection {collection_id}"
            )
            for ds in data_sources:
                if "config" in ds:
                    try:
                        ds["config"] = decrypt_dict(ds["config"])
                        logger.debug(
                            f"Decrypted config for data source ID: {ds.get('id', 'unknown')}"
                        )
                    except Exception as decryption_error:
                        logger.warning(
                            f"Could not decrypt config for data source: {decryption_error}"
                        )
                        ds["config"] = {}  # Fallback or redacted config
            return data_sources
        except Exception as e:
            logger.exception(
                f"Failed to list data sources for collection {collection_id}: {e}"
            )
            raise DataSourceListException(f"Failed to list data sources: {str(e)}")

    def generate_sas_urls(self, folder_name: str, file_names: list) -> Dict[str, str]:
        """
        Generate presigned URLs for uploading files to S3.
        """
        logger.info(f"Generating presigned URLs for folder_name={folder_name}")
        try:
            urls = {}
            for file_name in file_names:
                object_key = f"{folder_name}/{file_name}"
                presigned_url, content_type = generate_presigned_upload_url(object_key)
                urls[file_name] = {"url": presigned_url, "content_type": content_type}
                logger.debug(
                    f"Presigned URL generated for {file_name}: {presigned_url}"
                )
            logger.info(f"Successfully generated {len(urls)} presigned URLs.")
            return urls
        except Exception as e:
            logger.exception("Presigned URL generation failed")
            raise SASUrlGenerationException(
                f"Failed to generate presigned URLs: {str(e)}"
            )

    def _get_collection_id_by_data_source(self, data_source_id: str) -> str | None:
        """
        Get the collection ID associated with a given data source ID
        """
        logger.info(f"Fetching collection ID for data source ID: {data_source_id}")
        try:
            items = fetch_items(self.table_name, "id", data_source_id)
            if items and len(items) > 0:
                collection_id = items[0]["collection_id"]
                logger.debug(
                    f"Found collection ID '{collection_id}' for data source ID: {data_source_id}"
                )
                return collection_id
            else:
                logger.warning(f"No data source found with ID: {data_source_id}")
                return None
        except Exception as e:
            logger.exception(
                f"Failed to fetch collection ID for data source {data_source_id}: {e}"
            )
            return None

    def _get_vector_store_by_collection(
        self, collection_id: str, user_id: str
    ) -> VectorStoreProtocol:
        """
        Get the vector store instance for a given collection ID
        """

        database_service = DatabaseService()
        vector_store = VectorStoreFactory.get_vector_store(
            collection_id, user_id, database_service
        )
        return vector_store

    def delete_data_sources_by_collection(
        self, collection_id: str, user_id: str
    ) -> None:
        """
        Delete all data sources associated with a given collection ID
        """
        logger.info(f"Deleting data sources for collection ID: {collection_id}")
        try:
            data_sources = fetch_items(
                settings.DATA_SOURCES_TABLE_NAME, "collection_id", collection_id
            )
            for data_source in data_sources:
                self.delete_data_source(data_source["id"], user_id)
            logger.debug(
                f"All data sources for collection ID {collection_id} deleted successfully."
            )
        except Exception as e:
            logger.exception(
                f"Failed to delete data sources for collection {collection_id}: {e}"
            )
            raise DataSourceDeletionException(
                f"Failed to delete data sources: {str(e)}"
            )
