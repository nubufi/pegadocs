import logging

from app.application.services.model_service import ModelService
from app.application.services.phase2_service import Phase2Service
from app.application.services.reader_service import ReaderService
from app.deps import get_task_service
from app.infra.config import settings
from app.presentation.controllers.embedding_controller import EmbeddingController
from app.presentation.schemas.embedding_schemas import EmbeddingRequest
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="embedding.orchestrate")
def run_embed_task(task_id: str, req_data: dict, user_id: str) -> None:
    task_svc = get_task_service()
    try:
        task_svc.create(task_id)
        task_svc.progress(task_id, 1)

        req = EmbeddingRequest(**req_data)
        metadata = dict(getattr(req, "additional_metadata", {}) or {})
        metadata["job_id"] = task_id
        req.additional_metadata = metadata

        reader_service = ReaderService()
        model_service = ModelService()
        controller = EmbeddingController(reader_service, model_service)

        task_svc.progress(task_id, 10)
        controller.embed_documents(request=req, user_id=user_id, job_id=task_id)
        task_svc.progress(task_id, 50)

        doc_keys = Phase2Service.list_document_keys(task_id)
        if not doc_keys:
            task_svc.complete(task_id, {"message": "No documents to embed"})
            return

        for key in doc_keys:
            process_document.delay(
                task_id=task_id,
                s3_key=key,
                collection_id=req_data["collection_id"],
                user_id=user_id,
                data_source_id=req_data["data_source_id"],
                chunk_size=req_data.get("chunk_size", settings.CHUNK_SIZE),
                chunk_overlap=req_data.get(
                    "chunk_overlap", settings.CHUNK_OVERLAP
                ),
            )

        task_svc.progress(task_id, 55)
        logger.info(
            "Fan-out complete: %d document tasks submitted for job %s",
            len(doc_keys),
            task_id,
        )
    except Exception as exc:
        logger.exception("Embedding orchestration task failed")
        task_svc.fail(task_id, type(exc).__name__, str(exc))


@celery_app.task(
    name="embedding.process_document",
    autoretry_for=(Exception,),
    max_retries=3,
    default_retry_delay=30,
)
def process_document(
    task_id: str,
    s3_key: str,
    collection_id: str,
    user_id: str,
    data_source_id: str,
    chunk_size: int,
    chunk_overlap: int,
) -> None:
    doc = Phase2Service.load_document_from_s3(s3_key)
    nodes = Phase2Service.chunk_document(doc, chunk_size, chunk_overlap)
    if not nodes:
        return

    doc_id = doc.doc_id or s3_key
    Phase2Service.record_expected_nodes(task_id, doc_id, len(nodes))
    Phase2Service.embed_and_store(nodes, collection_id, user_id)
    Phase2Service.record_node_statuses(
        task_id, doc_id, data_source_id, nodes, "success"
    )