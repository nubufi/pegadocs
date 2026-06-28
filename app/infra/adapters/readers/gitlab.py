from typing import Any, Dict, List, Sequence

from gitlab import Gitlab
from llama_index.core import Document
from llama_index.readers.gitlab import GitLabRepositoryReader
from app.application.exceptions import InvalidDataSourceConfigException
from app.application.protocols.reader_protocol import ReaderProtocol


class GitlabReader(ReaderProtocol):
    def __init__(
        self, data_source_id: str, config: dict, chunk_size: int, chunk_overlap: int
    ):
        self.validate_config(config)
        self.data_source_id = data_source_id
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.project_id = config["project_id"]
        self.branch = config["branch"]
        self.client = Gitlab(config["host"], private_token=config["private_token"])
        self.inclusion_rules = config["inclusion_rules"]
        self.exclusion_rules = config["exclusion_rules"]
        self.key = "file_path"
        self.reader = self._get_reader()
        self.inclusion_rules = config.get("inclusion_rules", [])
        self.exclusion_rules = config.get("exclusion_rules", [])

    def _get_reader(self) -> GitLabRepositoryReader:
        return GitLabRepositoryReader(
            self.client,
            project_id=self.project_id,
        )

    def validate_config(self, config: dict):
        required_keys = [
            "host",
            "project_id",
            "private_token",
            "branch",
            "inclusion_rules",
            "exclusion_rules",
        ]
        if not all(key in config for key in required_keys):
            raise InvalidDataSourceConfigException(
                "GitlabReader requires 'inclusion_rules','exclusion_rules','host', 'project_id', 'private_token', and 'branch' in config."
            )

    def customize_metadata(
        self, document: Document, additional_metadata: Dict[str, Any]
    ) -> Document:
        document.metadata["data_source_id"] = self.data_source_id
        document.excluded_llm_metadata_keys.append("data_source_id")
        document.metadata.update(additional_metadata)

        return document

    def get_documents(self, additional_metadata: Dict[str, Any]) -> Sequence[Document]:
        documents = self.reader.load_data(
            ref=self.branch,
            recursive=True,
        )
        for document in documents:
            self.customize_metadata(document, additional_metadata)

        documents = self.apply_rules(
            documents=documents,
            key=self.key,
        )
        return documents

    def list_resources(self) -> List[str]:
        return self.list_resources_by_documents()
