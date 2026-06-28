from app.application.services.reader_service import ReaderService
from app.application.services.model_service import ModelService
import logging

from app.presentation.controllers.embedding_controller import EmbeddingController
from app.presentation.schemas.embedding_schemas import EmbeddingRequest
from app.application.services.task_service import TaskService

logger = logging.getLogger(__name__)


def run_embed_task(
    task_id: str, req: EmbeddingRequest, user_id: str, task_svc: TaskService
) -> None:
    """Blocking worker function executed by FastAPI BackgroundTasks."""
    try:
        # idempotent safety
        task_svc.create(task_id)
        task_svc.progress(task_id, 1)

        reader_service = ReaderService()
        model_service = ModelService()
        controller = EmbeddingController(reader_service, model_service)

        task_svc.progress(task_id, 10)

        metadata = dict(getattr(req, "additional_metadata", {}) or {})
        metadata["job_id"] = task_id
        req.additional_metadata = metadata

        controller.embed_documents(request=req, user_id=user_id, job_id=task_id)

        task_svc.progress(task_id, 50)
    except Exception as exc:
        logger.exception("Embedding background task failed")
        task_svc.fail(task_id, type(exc).__name__, str(exc))
