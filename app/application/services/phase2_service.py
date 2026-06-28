import json
from typing import List, Sequence

import boto3
from loguru import logger
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import BaseNode, Document, TextNode

from app.application.services.database_service import DatabaseService
from app.application.services.model_service import ModelService
from app.infra.config import settings
from app.infra.factories.models import ModelFactory
from app.infra.factories.vector_store import VectorStoreFactory
from app.infra.utils.collection_utils import get_embedding_model_id_by_collection_id
from app.infra.utils.embedding_job_utils import _sanitize_identifier

_dynamodb = boto3.resource("dynamodb", region_name=settings.AWS_REGION)
_file_status_table = _dynamodb.Table(settings.FILE_STATUS_TABLE_NAME)
_nodes_table = _dynamodb.Table(settings.NODES_TABLE_NAME)
_s3 = boto3.client("s3", region_name=settings.AWS_REGION)


class Phase2Service:
    """Handles Phase 2 of embedding: chunk, embed, store, track status."""

    @staticmethod
    def list_document_keys(job_id: str) -> List[str]:
        bucket = settings.S3_EMBEDDING_BUCKET_NAME
        if not bucket:
            raise ValueError("S3_EMBEDDING_BUCKET_NAME is not configured.")
        prefix = f"{_sanitize_identifier(job_id)}/"
        keys: List[str] = []
        paginator = _s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                if key.endswith(".json"):
                    keys.append(key)
        return keys

    @staticmethod
    def load_document_from_s3(key: str) -> Document:
        bucket = settings.S3_EMBEDDING_BUCKET_NAME
        if not bucket:
            raise ValueError("S3_EMBEDDING_BUCKET_NAME is not configured.")
        resp = _s3.get_object(Bucket=bucket, Key=key)
        data = json.loads(resp["Body"].read().decode("utf-8"))
        return Document(
            text=data.get("text", ""),
            doc_id=data.get("id_"),
            metadata=data.get("metadata", {}),
            excluded_embed_metadata_keys=data.get(
                "excluded_embed_metadata_keys", []
            ),
            excluded_llm_metadata_keys=data.get(
                "excluded_llm_metadata_keys", []
            ),
            relationships=data.get("relationships", {}),
        )

    @staticmethod
    def chunk_document(
        doc: Document, chunk_size: int, chunk_overlap: int
    ) -> List[TextNode]:
        parser = SentenceSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        nodes = parser.get_nodes_from_documents([doc])
        return nodes

    @staticmethod
    def record_expected_nodes(job_id: str, doc_id: str, count: int) -> None:
        _file_status_table.put_item(
            Item={
                "job_id": job_id,
                "doc_id": doc_id,
                "number_of_nodes": count,
            }
        )

    @staticmethod
    def record_node_statuses(
        job_id: str,
        doc_id: str,
        data_source_id: str,
        nodes: Sequence[BaseNode],
        status: str,
    ) -> None:
        with _nodes_table.batch_writer() as batch:
            for node in nodes:
                token_size = len(node.text) // 4 if node.text else 0
                batch.put_item(
                    Item={
                        "job_id": job_id,
                        "doc_id": doc_id,
                        "data_source_id": data_source_id,
                        "token_size": token_size,
                        "status": status,
                    }
                )

    @staticmethod
    def embed_and_store(
        nodes: Sequence[BaseNode],
        collection_id: str,
        user_id: str,
    ) -> None:
        model_service = ModelService()
        model_factory = ModelFactory(model_service)
        embedding_model_id = get_embedding_model_id_by_collection_id(collection_id)
        priced_model = model_factory.get_embedding_model(embedding_model_id)
        embedding_model = priced_model.model

        database_service = DatabaseService()
        vector_store = VectorStoreFactory.get_vector_store(
            collection_id, user_id, database_service
        )
        vector_store.create_index(nodes, embedding_model)
        logger.info(
            "Embedded %d nodes into vector store for collection %s",
            len(nodes),
            collection_id,
        )