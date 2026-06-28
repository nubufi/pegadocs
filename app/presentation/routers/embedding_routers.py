import uuid
from typing import Dict

from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.responses import JSONResponse

from app.application.protocols.task_store import TaskStatus
from app.application.services.embedding_job_monitor import (
    EmbeddingJobMonitor,
)
from app.application.services.task_service import TaskService
from app.deps import get_task_service
from app.infra.auth import get_user
from app.infra.config import settings
from app.infra.utils.supabase_utils import fetch_items
from app.presentation.schemas.embedding_schemas import EmbeddingRequest
from app.presentation.schemas.task_schemas import (
    TaskCreationResponse,
    TaskStatusResponse,
)
from app.tasks.embedding import run_embed_task

embedding_router = APIRouter()
_job_monitor = EmbeddingJobMonitor()


def _normalize_task_payload(task_id: str, state: Dict) -> Dict:
    payload = dict(state)
    status = payload.get("status")
    if isinstance(status, TaskStatus):
        payload["status"] = status.value
    elif status is None:
        payload["status"] = TaskStatus.UNKNOWN.value
    if "error" not in payload and (
        "error_type" in payload or "error_message" in payload
    ):
        payload["error"] = {
            "error_type": payload.pop("error_type", "UnknownError"),
            "error_message": payload.pop("error_message", "Unknown error"),
        }
    payload["task_id"] = task_id
    return payload


@embedding_router.get(
    "/embed/{task_id}",
    summary="Finalize embedding job",
    response_model=TaskStatusResponse,
    tags=["embedding"],
)
def finalize_embedding_job(
    task_id: str,
    task_svc: TaskService = Depends(get_task_service),
):
    current_state = task_svc.status(task_id)
    payload = _normalize_task_payload(task_id, current_state)
    if payload["status"] == TaskStatus.DONE.value:
        return payload

    summary = _job_monitor.load_summary(task_id)
    progress = summary.progress_percent
    if progress is not None:
        task_svc.progress(task_id, progress)
        current_state = task_svc.status(task_id)
        payload = _normalize_task_payload(task_id, current_state)

    if summary.failure_rate > 0.10:
        task_svc.fail(
            task_id,
            "TooManyFailures",
            f"Embedding job failed: {summary.failed_nodes_count} out of {summary.total_actual_nodes} nodes failed ({summary.failure_rate:.1%}).",
        )
        final_state = task_svc.status(task_id)
        return _normalize_task_payload(task_id, final_state)

    if not summary.ready:
        pending = summary.pending_documents
        if pending:
            payload.setdefault("result", {})
            payload["result"]["pending_documents"] = pending
        payload["progress"] = summary.progress_percent
        return payload

    data_source_id = summary.data_source_id
    if not data_source_id:
        return payload

    data_sources = fetch_items(settings.DATA_SOURCES_TABLE_NAME, "id", data_source_id)
    if not data_sources:
        task_svc.fail(
            task_id,
            "DataSourceNotFound",
            f"Data source {data_source_id} not found while finalizing job.",
        )
        final_state = task_svc.status(task_id)
        return _normalize_task_payload(task_id, final_state)

    total_tokens = summary.total_tokens

    result_summary = {
        "message": "Embedding job finalized",
        "total_tokens": total_tokens,
    }
    task_svc.complete(task_id, result_summary)
    final_state = task_svc.status(task_id)
    return _normalize_task_payload(task_id, final_state)


@embedding_router.post(
    "/embed",
    summary="Embed documents from data source",
    response_model=TaskCreationResponse,
    tags=["embedding"],
)
def embed(
    input: EmbeddingRequest,
    background: BackgroundTasks,
    user_id: str = Depends(get_user),
    task_svc: TaskService = Depends(get_task_service),
):
    # 1) generate task id
    task_id = str(uuid.uuid4())

    # 2) create a monitor record immediately so clients can poll
    task_svc.create(task_id)
    task_svc.progress(task_id, 1)

    # 3) schedule background work
    background.add_task(run_embed_task, task_id, input, user_id, task_svc)

    # 4) return 202 with task id
    return JSONResponse(content={"task_id": task_id}, status_code=202)
