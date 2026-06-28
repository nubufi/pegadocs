from typing import Any, Dict, List
from llama_index.core import Document
from llama_index.readers.azstorage_blob import AzStorageBlobReader
from llama_index.readers.file import PDFReader

from app.application.exceptions import InvalidDataSourceConfigException
from app.application.protocols.reader_protocol import ReaderProtocol


class AzureStorageBlobReader(ReaderProtocol):
    """Embedding method for processing files"""

    def __init__(
        self,
        data_source_id: str,
        config: Dict[str, Any],
        chunk_size: int,
        chunk_overlap: int,
    ):
        self.validate_config(config)
        self.data_source_id = data_source_id
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.config: Dict[str, Any] = config
        self.key = "name"
        self.reader = self._get_reader()
        self.inclusion_rules = config.get("inclusion_rules", [])
        self.exclusion_rules = config.get("exclusion_rules", [])

    def _get_reader(self) -> AzStorageBlobReader:
        account_name = self.config["account_name"]
        account_key = self.config["account_key"]
        connection_string = self._get_connection_string(
            account_name=account_name, account_key=account_key
        )
        return AzStorageBlobReader(
            container_name=self.config["container_name"],
            account_url=self.config["account_url"],
            connection_string=connection_string,
            name_starts_with=self.config.get("folder_path"),
            file_extractor={".pdf": PDFReader(return_full_document=True)},
        )

    def validate_config(self, config: dict):
        required_keys = [
            "container_name",
            "account_url",
            "account_name",
            "account_key",
            "inclusion_rules",
            "exclusion_rules",
        ]
        for key in required_keys:
            if key not in config:
                raise InvalidDataSourceConfigException(
                    f"AzureStorageBlobReader requires '{key}' in config."
                )

    @staticmethod
    def _get_connection_string(account_name: str, account_key: str) -> str:
        return f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key}"

    def customize_metadata(
        self, document: Document, additional_metadata: Dict[str, Any]
    ) -> Document:
        allowed_keys = [
            "file_name",
            "container",
            "size",
        ]
        for key in list(document.metadata.keys()):
            if key not in allowed_keys:
                del document.metadata[key]
        document.metadata["data_source_id"] = self.data_source_id
        document.excluded_llm_metadata_keys = ["data_source_id"]
        document.excluded_embed_metadata_keys = ["data_source_id"] + allowed_keys
        document.metadata.update(additional_metadata)

        return document

    def get_documents(self, additional_metadata: Dict[str, Any]) -> List[Document]:
        documents = self.reader.load_data()
        for document in documents:
            self.customize_metadata(document, additional_metadata)

        return documents
