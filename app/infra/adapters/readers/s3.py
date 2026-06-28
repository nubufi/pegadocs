from typing import Any, Dict, List, Sequence

from llama_index.core import Document, SimpleDirectoryReader
from llama_index.readers.file import PDFReader
from s3fs import S3FileSystem

from app.application.exceptions import InvalidDataSourceConfigException
from app.application.protocols.reader_protocol import ReaderProtocol


class AWSS3Reader(ReaderProtocol):
    """Embedding method for processing files from S3"""

    def __init__(
        self, data_source_id: str, config: dict, chunk_size: int, chunk_overlap: int
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

    def _get_reader(self) -> SimpleDirectoryReader:
        s3_fs = S3FileSystem(
            anon=False,
            key=self.config["aws_access_key_id"],
            secret=self.config["aws_secret_access_key"],
            client_kwargs={"region_name": self.config["region"]},
        )
        keys = self.config.get("key")
        bucket_name = self.config["bucket_name"]
        recursive = self.config.get("recursive", True)
        prefix = self.config.get("prefix", "")

        if keys is not None:
            return SimpleDirectoryReader(
                input_files=[f"{bucket_name}/{key}" for key in keys],
                fs=s3_fs,
                recursive=recursive,
                file_extractor={".pdf": PDFReader(return_full_document=True)},
            )
        else:
            return SimpleDirectoryReader(
                input_dir=f"{bucket_name}/{prefix}",
                fs=s3_fs,
                recursive=recursive,
                file_extractor={".pdf": PDFReader(return_full_document=True)},
            )

    def validate_config(self, config: dict):
        required_keys = [
            "aws_access_key_id",
            "aws_secret_access_key",
            "region",
            "bucket_name",
            "inclusion_rules",
            "exclusion_rules",
        ]
        if not all(key in config for key in required_keys):
            raise InvalidDataSourceConfigException(
                "AWSS3Reader requires 'aws_access_key_id', 'aws_secret_access_key', "
                "'region', 'bucket_name', 'inclusion_rules' and 'exclusion_rules' in config."
            )

    def customize_metadata(
        self, document: Document, additional_metadata: Dict[str, Any]
    ) -> Document:
        document.excluded_llm_metadata_keys.append("data_source_id")
        document.metadata["data_source_id"] = self.data_source_id
        document.metadata.update(additional_metadata)

        return document

    def get_documents(self, additional_metadata: Dict[str, Any]) -> Sequence[Document]:
        documents = self.reader.load_data()

        for document in documents:
            self.customize_metadata(document, additional_metadata)

        documents = self.apply_rules(
            documents=documents,
            key=self.key,
        )
        return documents
