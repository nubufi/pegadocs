from typing import Any, Dict, List, Sequence
from llama_index.core import Document
from llama_index.readers.web import SpiderWebReader

from app.application.exceptions import InvalidDataSourceConfigException
from app.application.protocols.reader_protocol import ReaderProtocol
from app.infra.config import settings


class WebReader(ReaderProtocol):
    """Embedding method for crawling websites"""

    def __init__(
        self, data_source_id: str, config: dict, chunk_size: int, chunk_overlap: int
    ):
        self.validate_config(config)

        self.data_source_id = data_source_id
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.website_url = config["website_url"]
        self.mode = config["mode"]
        self.inclusion_rules = config["inclusion_rules"]
        self.exclusion_rules = config["exclusion_rules"]
        self.key = "pathname"
        self.reader = self._get_reader()
        self.inclusion_rules = config.get("inclusion_rules", [])
        self.exclusion_rules = config.get("exclusion_rules", [])

    def _get_reader(self) -> SpiderWebReader:
        return SpiderWebReader(
            api_key=settings.SPIDER_WEB_API_KEY,
            mode=self.mode,
        )

    def validate_config(self, config: dict):
        required_keys = ["website_url", "mode", "inclusion_rules", "exclusion_rules"]
        if not all(key in config for key in required_keys):
            raise InvalidDataSourceConfigException(
                "WebReader requires 'website_url', 'mode', 'inclusion_rules' and 'exclusion_rules' in config."
            )

    def customize_metadata(
        self, document: Document, additional_metadata: Dict[str, Any]
    ) -> Document:
        document.metadata = {
            "description": document.metadata.get("description", ""),
            "final_url": document.metadata.get("final_url", ""),
            "data_source_id": self.data_source_id,
            **additional_metadata,
        }
        return document

    def get_documents(self, additional_metadata: Dict[str, Any]) -> Sequence[Document]:
        documents = self.reader.load_data(url=self.website_url)
        for document in documents:
            self.customize_metadata(document, additional_metadata)

        documents = self.apply_rules(
            documents=documents,
            key=self.key,
        )

        return documents

    def list_resources(self) -> List[str]:
        return self.list_resources_by_documents()
