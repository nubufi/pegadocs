from typing import Any, Dict, Sequence
from llama_index.core import Document
from llama_index.readers.file import PDFReader
from llama_index.readers.microsoft_onedrive import OneDriveReader as ODriveReader

from app.application.exceptions import InvalidDataSourceConfigException
from app.application.protocols.reader_protocol import ReaderProtocol


class OneDriveReader(ReaderProtocol):
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
        self.key = "file_path"
        self.reader = self._get_reader()
        self.inclusion_rules = config.get("inclusion_rules", [])
        self.exclusion_rules = config.get("exclusion_rules", [])

    def _get_reader(self) -> ODriveReader:
        return ODriveReader(
            client_id=self.config["client_id"],
            client_secret=self.config["client_secret"],
            tenant_id=self.config["tenant_id"],
            userprincipalname=self.config["user_principal_name"],
            folder_path=self.config["folder_path"],
            file_extractor={".pdf": PDFReader(return_full_document=True)},
        )

    def validate_config(self, config: dict):
        required_keys = [
            "client_id",
            "client_secret",
            "tenant_id",
            "user_principal_name",
            "folder_path",
            "inclusion_rules",
            "exclusion_rules",
        ]
        for key in required_keys:
            if key not in config:
                raise InvalidDataSourceConfigException(
                    f"OneDriveReader requires '{key}' in config."
                )

    def customize_metadata(
        self, document: Document, additional_metadata: Dict[str, Any]
    ) -> Document:
        document.metadata["data_source_id"] = self.data_source_id
        document.excluded_llm_metadata_keys.append("data_source_id")
        document.metadata.update(additional_metadata)

        return document

    def get_documents(self, additional_metadata: Dict[str, Any]) -> Sequence[Document]:
        folder_path = self.config.get("folder_path") or None
        documents = self.reader.load_data(folder_path=folder_path)
        if not documents:
            return []
        for document in documents:
            self.customize_metadata(document, additional_metadata)

        documents = self.apply_rules(
            documents=documents,
            key=self.key,
        )
        return documents
