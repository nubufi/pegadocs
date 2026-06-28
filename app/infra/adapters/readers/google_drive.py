from typing import Any, Dict, List, Sequence
from llama_index.core import Document
from llama_index.readers.file import PDFReader
from llama_index.readers.google import GoogleDriveReader as GDriveReader

from app.application.exceptions import (
    InvalidDataSourceConfigException,
)
from app.application.protocols.reader_protocol import ReaderProtocol


class GoogleDriveReader(ReaderProtocol):
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
        self.key = "file path"
        self.reader: GDriveReader = self._get_reader()
        self.inclusion_rules = config.get("inclusion_rules", [])
        self.exclusion_rules = config.get("exclusion_rules", [])

    def _get_reader(self) -> GDriveReader:
        service_account_dict = self.config["service_account_dict"]
        if "folder_id" in self.config:
            return GDriveReader(
                folder_id=self.config["folder_id"],
                service_account_key=service_account_dict,
                file_extractor={".pdf": PDFReader(return_full_document=True)},
            )
        elif "drive_id" in self.config:
            return GDriveReader(
                drive_id=self.config["drive_id"],
                service_account_key=service_account_dict,
                file_extractor={".pdf": PDFReader(return_full_document=True)},
            )
        else:
            return GDriveReader(
                file_ids=self.config["file_ids"],
                service_account_key=service_account_dict,
                file_extractor={".pdf": PDFReader(return_full_document=True)},
            )

    def validate_config(self, config: dict):
        required_keys = [
            "service_account_dict",
            "inclusion_rules",
            "exclusion_rules",
        ]
        for key in required_keys:
            if key not in config:
                raise InvalidDataSourceConfigException(
                    f"GoogleDriveReader requires '{key}' in config."
                )

        if any(k not in config for k in ["folder_id", "drive_id", "file_ids"]):
            raise InvalidDataSourceConfigException(
                "GoogleDriveReader requires at least one of 'folder_id', 'drive_id' or 'file_ids' in config."
            )

        required_service_account_keys = [
            "type",
            "project_id",
            "private_key_id",
            "private_key",
            "client_email",
            "client_id",
            "auth_uri",
            "token_uri",
            "auth_provider_x509_cert_url",
            "client_x509_cert_url",
            "universe_domain",
        ]

        for key in required_service_account_keys:
            if key not in config["service_account_dict"]:
                raise InvalidDataSourceConfigException(
                    f"GoogleDriveReader requires '{key}' in 'service_account'."
                )

    def customize_metadata(
        self, document: Document, additional_metadata: Dict[str, Any]
    ) -> Document:
        document.metadata["data_source_id"] = self.data_source_id
        document.excluded_llm_metadata_keys.append("data_source_id")
        document.metadata.update(additional_metadata)

        return document

    def get_documents(self, additional_metadata: Dict[str, Any]) -> Sequence[Document]:
        documents = self.reader.load_data()

        if not documents:
            return []
        for document in documents:
            self.customize_metadata(document, additional_metadata)

        documents = self.apply_rules(
            documents=documents,
            key=self.key,
        )
        return documents

    def list_resources(self) -> List[str]:
        return self.list_resources_by_documents()
