from typing import Any, Dict, List, Sequence

from llama_index.core import Document
from llama_index.readers.jira import JiraReader as JR

from app.application.exceptions import InvalidDataSourceConfigException
from app.application.protocols.reader_protocol import ReaderProtocol


class JiraReader(ReaderProtocol):
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
        self.key = ""
        self.reader = self._get_reader()
        self.inclusion_rules = config.get("inclusion_rules", [])
        self.exclusion_rules = config.get("exclusion_rules", [])

    def _get_reader(self) -> JR:
        return JR(
            email=self.config["email"],
            api_token=self.config["api_token"],
            server_url=self.config["server_url"],
        )

    def validate_config(self, config: dict):
        required_keys = ["email", "api_token", "server_url", "project"]
        for key in required_keys:
            if key not in config:
                raise InvalidDataSourceConfigException(
                    f"JiraReader requires '{key}' in config."
                )

    def customize_metadata(
        self, document: Document, additional_metadata: Dict[str, Any]
    ) -> Document:
        document.metadata["data_source_id"] = self.data_source_id
        document.excluded_llm_metadata_keys.append("data_source_id")
        document.metadata.update(additional_metadata)

        return document

    def get_documents(self, additional_metadata: Dict[str, Any]) -> Sequence[Document]:
        documents = self.reader.load_data(f"project = {self.config['project']}")

        for document in documents:
            self.customize_metadata(document, additional_metadata)

        return documents

    def list_resources(self) -> List[str]:
        return self.list_resources_by_documents()
