from typing import Any, Dict, List, Sequence
from llama_index.core import Document
from llama_index.readers.github import GithubClient, GithubRepositoryReader

from app.application.exceptions import InvalidDataSourceConfigException
from app.application.protocols.reader_protocol import ReaderProtocol


class GithubReader(ReaderProtocol):
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
        self.owner = config["owner"]
        self.repo = config["repo"]
        self.branch = config["branch"]
        self.use_parser = True
        self.github_token = config["github_token"]
        self.inclusion_rules = config["inclusion_rules"]
        self.exclusion_rules = config["exclusion_rules"]
        self.key = "pathname"
        self.reader = self._get_reader()
        self.inclusion_rules = config.get("inclusion_rules", [])
        self.exclusion_rules = config.get("exclusion_rules", [])

    def _get_reader(self) -> GithubRepositoryReader:
        github_client = GithubClient(
            github_token=self.github_token,
        )
        return GithubRepositoryReader(
            github_client=github_client,
            owner=self.owner,
            repo=self.repo,
            use_parser=self.use_parser,
        )

    def validate_config(self, config: dict):
        required_keys = [
            "owner",
            "repo",
            "github_token",
            "branch",
            "inclusion_rules",
            "exclusion_rules",
        ]
        if not all(key in config for key in required_keys):
            raise InvalidDataSourceConfigException(
                "GithubReader requires 'owner', 'repo', 'github_token', 'branch', "
                "'inclusion_rules', 'exclusion_rules' in config."
            )

    def customize_metadata(
        self, document: Document, additional_metadata: Dict[str, Any]
    ) -> Document:
        document.metadata["data_source_id"] = self.data_source_id
        document.excluded_llm_metadata_keys.append("data_source_id")
        document.metadata.update(additional_metadata)

        return document

    def get_documents(self, additional_metadata: Dict[str, Any]) -> Sequence[Document]:
        documents = self.reader.load_data(branch=self.branch)
        for document in documents:
            self.customize_metadata(document, additional_metadata)

        documents = self.apply_rules(
            documents=documents,
            key=self.key,
        )
        return documents

    def list_resources(self) -> List[str]:
        return self.list_resources_by_documents()
