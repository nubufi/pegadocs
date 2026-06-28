from typing import Any, Dict, List, Sequence
from urllib.parse import unquote, urlparse

from llama_index.core import Document
from llama_index.readers.file import PDFReader
from llama_index.readers.microsoft_sharepoint import SharePointReader as SPReader

from app.application.exceptions import InvalidDataSourceConfigException
from app.application.protocols.reader_protocol import ReaderProtocol


class SharePointReader(ReaderProtocol):
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
        self.reader = None
        self.inclusion_rules = config.get("inclusion_rules", [])
        self.exclusion_rules = config.get("exclusion_rules", [])

    def _get_reader(self, lib_name: str) -> SPReader:
        return SPReader(
            client_id=self.config["client_id"],
            client_secret=self.config["client_secret"],
            tenant_id=self.config["tenant_id"],
            sharepoint_site_name=self.config["sharepoint_site_name"],
            drive_name=lib_name,
            file_extractor={".pdf": PDFReader(return_full_document=True)},
        )

    def validate_config(self, config: dict):
        required_keys = [
            "client_id",
            "client_secret",
            "tenant_id",
            "library_names",
            "folder_path",
            "sharepoint_site_name",
            "inclusion_rules",
            "exclusion_rules",
        ]
        for key in required_keys:
            if key not in config:
                raise InvalidDataSourceConfigException(
                    f"OneDriveReader requires '{key}' in config."
                )

    @staticmethod
    def get_sp_file_path(url: str) -> str:
        """
        Return 'Library/folder_path/file_name' from a SharePoint file URL.
        If no folder, returns 'Library/file_name'.
        """
        parsed = urlparse(url)
        # Decode %20 etc.
        parts = unquote(parsed.path).strip("/").split("/")

        # Expect at least /sites/<site>/<library>/<file or folder/...>
        if len(parts) < 4 or parts[0] != "sites":
            raise ValueError(f"Unexpected SharePoint path: {parsed.path}")

        # Drop 'sites' and site name → keep from library onward
        library_and_rest = parts[2:]

        return "/".join(library_and_rest)

    def customize_metadata(
        self, document: Document, additional_metadata: Dict[str, Any]
    ) -> Document:
        document.metadata["data_source_id"] = self.data_source_id
        document.excluded_llm_metadata_keys.append("data_source_id")
        document.metadata["file_path"] = self.get_sp_file_path(
            document.metadata.get("url", "")
        )
        document.metadata.update(additional_metadata)

        return document

    def get_documents(self, additional_metadata: Dict[str, Any]) -> Sequence[Document]:
        documents = []
        for lib_name in self.config["library_names"]:
            reader = self._get_reader(lib_name)
            folder_path = self.config.get("folder_path") or None
            documents.extend(reader.load_data(sharepoint_folder_path=folder_path))

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
        docs = []
        for lib_name in self.config["library_names"]:
            reader = self._get_reader(lib_name)
            folder_path = self.config.get("folder_path") or None
            docs.extend(reader.list_resources(sharepoint_folder_path=folder_path))

        if not self.inclusion_rules and not self.exclusion_rules:
            return docs

        inclusion_patterns = self._compile_patterns(self.inclusion_rules)
        exclusion_patterns = self._compile_patterns(self.exclusion_rules)
        filtered_docs = []
        for doc in docs:
            if any(pattern.search(doc) for pattern in inclusion_patterns) and not any(
                pattern.search(doc) for pattern in exclusion_patterns
            ):
                filtered_docs.append(doc)

        return filtered_docs
