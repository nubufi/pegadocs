from typing import Any, Dict, List, Sequence
from llama_index.core import Document

from app.application.exceptions import InvalidDataSourceConfigException
from app.application.protocols.reader_protocol import ReaderProtocol
from app.infra.config import settings
from app.infra.adapters.readers.s3 import AWSS3Reader


class FileReader(ReaderProtocol):
    """Embedding method for processing files"""

    def __init__(
        self, data_source_id: str, config: dict, chunk_size: int, chunk_overlap: int
    ):
        self.data_source_id = data_source_id
        self.config = config
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.s3_bucket_name = settings.S3_DATA_SOURCE_BUCKET_NAME
        self.aws_region = settings.AWS_REGION
        self.aws_access_key_id = settings.AWS_ACCESS_KEY_ID
        self.validate_config(config)

        self.reader = self.get_reader()

    def validate_config(self, config: dict):
        required_keys = ["folder_name"]
        for key in required_keys:
            if key not in config:
                raise InvalidDataSourceConfigException(
                    f"FileReader requires '{key}' in config."
                )

    def customize_metadata(
        self, document: Document, additional_metadata: Dict[str, Any]
    ) -> Document:
        allowed_keys = ["page_label", "file_name", "file_size"]
        for key in list(document.metadata.keys()):
            if key not in allowed_keys:
                del document.metadata[key]
        document.metadata["data_source_id"] = self.data_source_id
        document.excluded_llm_metadata_keys.append("data_source_id")
        document.metadata.update(additional_metadata)

        return document

    def get_reader(self) -> AWSS3Reader:
        return AWSS3Reader(
            data_source_id=self.data_source_id,
            config={
                "aws_access_key_id": self.aws_access_key_id,
                "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
                "region": self.aws_region,
                "bucket_name": self.s3_bucket_name,
                "prefix": self.config["folder_name"],
                "recursive": True,
                "inclusion_rules": [],
                "exclusion_rules": [],
            },
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

    def get_documents(self, additional_metadata: Dict[str, Any]) -> Sequence[Document]:
        documents = self.reader.get_documents({})
        for document in documents:
            self.customize_metadata(document, additional_metadata)

        return documents

    @staticmethod
    def _remove_prefix(text: str) -> str:
        return "/".join(text.split("/", 2)[2:]) if "/" in text else text

    def list_resources(self) -> List[str]:
        return [self._remove_prefix(t) for t in self.reader.list_resources()]
