import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Sequence

from dropbox import Dropbox
from dropbox.files import FileMetadata
from llama_index.core import Document
from llama_index.readers.file import PDFReader
from llama_index.readers.file.docs.base import DocxReader
from llama_index.readers.file.markdown import MarkdownReader
from llama_index.readers.file.tabular.base import PandasCSVReader, PandasExcelReader
from llama_index.readers.legacy_office import LegacyOfficeReader


from app.application.exceptions import (
    InvalidDataSourceConfigException,
    OperationFailedException,
)
from app.application.protocols.reader_protocol import ReaderProtocol

TEMP_DIR = tempfile.gettempdir()


class DropboxReader(ReaderProtocol):
    def __init__(
        self,
        data_source_id: str,
        config: dict,
        chunk_size: int,
        chunk_overlap: int,
    ):
        self.validate_config(config)

        self.data_source_id = data_source_id
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.client = Dropbox(config["access_token"])
        self.folder_path = config["folder_path"]
        self.inclusion_rules = config["inclusion_rules"]
        self.exclusion_rules = config["exclusion_rules"]
        self.key = "file_path"
        self.reader = None
        self.inclusion_rules = config.get("inclusion_rules", [])
        self.exclusion_rules = config.get("exclusion_rules", [])

    def validate_config(self, config: dict):
        required_keys = [
            "access_token",
            "folder_path",
            "inclusion_rules",
            "exclusion_rules",
        ]
        if not all(key in config for key in required_keys):
            raise InvalidDataSourceConfigException(
                "DropboxReader requires 'inclusion_rules','exclusion_rules','access_token' and 'folder_path' in config."
            )

    @staticmethod
    def create_document_from_file(file_path) -> Document | None:
        ext_to_reader = {
            ".pdf": PDFReader(return_full_document=True),
            ".docx": DocxReader(),
            ".doc": LegacyOfficeReader(),
            ".csv": PandasCSVReader(),
            ".txt": None,
            ".html": None,
            ".xlsx": PandasExcelReader(),
            ".md": MarkdownReader(),
        }
        ext = Path(file_path).suffix.lower()
        reader = ext_to_reader.get(ext)
        if reader is None:
            return None
        docs = reader.load_data(Path(file_path))
        return docs[0] if docs else None

    def customize_metadata(
        self, document: Document, additional_metadata: Dict[str, Any]
    ) -> Document:
        document.excluded_llm_metadata_keys.append("data_source_id")
        document.metadata = {
            **additional_metadata,
            "data_source_id": self.data_source_id,
        }
        return document

    def create_document_from_entry(
        self, entry, additional_metadata: Dict[str, Any]
    ) -> Document | None:
        if not isinstance(entry, FileMetadata):
            return None

        file_path = entry.path_display
        file_name = entry.name

        try:
            _, response = self.client.files_download(file_path)
            content = response.content
            with open(os.path.join(TEMP_DIR, file_name), "wb") as f:
                f.write(content)

            doc = self.create_document_from_file(os.path.join(TEMP_DIR, file_name))
            if doc is None:
                return None
            self.customize_metadata(
                doc,
                {
                    **additional_metadata,
                    "file_path": file_path,
                    "file_name": file_name,
                    "last_modified": entry.client_modified.isoformat(),
                },
            )
            os.remove(os.path.join(TEMP_DIR, file_name))  # Clean up temp file
            return doc
        except:
            return None

    def get_documents(self, additional_metadata: Dict[str, Any]) -> Sequence[Document]:
        documents = []

        if self.folder_path != "" and not self.folder_path.startswith("/"):
            self.folder_path = "/" + self.folder_path
        try:
            result = self.client.files_list_folder(
                path=self.folder_path, recursive=True
            )
        except Exception as e:
            raise OperationFailedException(
                f"Failed to list Dropbox folder: {str(e)}"
            ) from e

        if result is None:
            return documents

        while True:
            for entry in result.entries:
                doc = self.create_document_from_entry(entry, additional_metadata)
                if doc is not None:
                    documents.append(doc)
            if not result.has_more:
                break
            result = self.client.files_list_folder_continue(result.cursor)

        documents = self.apply_rules(
            documents=documents,
            key=self.key,
        )
        return documents

    def list_resources(self) -> List[str]:
        return self.list_resources_by_documents()
