import re
from re import Pattern
from typing import Any, Dict, List, Protocol, Sequence

from llama_index.core.schema import Document

from app.infra.utils.embedding_job_utils import persist_documents_for_job


class ReaderProtocol(Protocol):
    """Common protocol for all embedding methods"""

    data_source_id: str
    chunk_size: int
    chunk_overlap: int
    config: Dict[str, str]
    inclusion_rules: List[str]
    exclusion_rules: List[str]
    reader: Any
    key: str

    def validate_config(self, config: dict) -> None:
        """Validate the configuration for the data source."""
        raise NotImplementedError

    def _get_file_path(self, document: Document) -> str:
        if document.metadata.get(self.key):
            return document.metadata.get(self.key, "")

        if document.metadata.get("metadata", {}).get(self.key):
            return document.metadata.get("metadata", {}).get(self.key)

        raise ValueError(f"{self.key} not found in document metadata.")

    def list_resources_by_documents(self) -> List[str]:
        docs = self.get_documents({})
        return [self._get_file_path(doc) for doc in docs]

    def list_resources(self) -> List[str]:
        docs = self.reader.list_resources()

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

    def get_documents(self, additional_metadata: Dict[str, Any]) -> Sequence[Document]:
        """Get documents from the data source."""
        raise NotImplementedError

    def customize_metadata(
        self, document: Document, additional_metadata: Dict[str, Any]
    ) -> Document:
        """Modify metadata of the nodes."""
        raise NotImplementedError

    @staticmethod
    def _compile_patterns(patterns: List[str]) -> List[Pattern]:
        compiled = []
        for pattern in patterns:
            try:
                compiled.append(re.compile(pattern))
            except re.error:
                raise ValueError(f"Invalid regex pattern: {pattern}")
        return compiled

    def apply_rules(
        self,
        documents: Sequence[Document],
        key: str,
    ) -> Sequence[Document]:
        """
        Apply inclusion and exclusion rules to the documents.
        This method filters documents based on the provided rules.

        Args:
            documents (Sequence[Document]): The list of documents to filter.
            inclusion_rules (List[str]): List of rules that must be included.
            exclusion_rules (List[str]): List of rules that must be excluded.
            key (str): The key in the document metadata to apply the rules on.

        Returns:
            Sequence[Document]: Filtered documents that match the rules.
        """
        if not self.inclusion_rules and not self.exclusion_rules or not key:
            return documents

        inclusion_patterns = self._compile_patterns(self.inclusion_rules)
        exclusion_patterns = self._compile_patterns(self.exclusion_rules)

        filtered_documents = []
        for document in documents:
            metadata_value = document.metadata.get(key, "")
            if any(
                pattern.search(metadata_value) for pattern in inclusion_patterns
            ) and not any(
                pattern.search(metadata_value) for pattern in exclusion_patterns
            ):
                filtered_documents.append(document)

        return filtered_documents

    def process(
        self,
        additional_metadata: Dict[str, Any],
        job_id: str,
    ) -> None:
        """Process document reading job"""
        documents = self.get_documents(additional_metadata)
        if not documents:
            raise ValueError("No documents found to process.")
        persist_documents_for_job(
            documents=documents,
            job_id=job_id,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )
