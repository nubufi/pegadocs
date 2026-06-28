import uuid

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import JSONResponse

from app.application.protocols.task_store import TaskStatus
from app.application.services.task_service import TaskService
from app.deps import get_task_service
from app.presentation.schemas.scanning_schemas import ScanningRequest
from app.presentation.schemas.task_schemas import (
    TaskCreationResponse,
    TaskStatusResponse,
)
from app.tasks.scan import run_scan_task

scanning_router = APIRouter()


@scanning_router.post(
    "/scan",
    summary="Scan files in the data source",
    response_model=TaskCreationResponse,
    tags=["scanning"],
)
def scan(
    input: ScanningRequest,
    background: BackgroundTasks,
    task_svc: TaskService = Depends(get_task_service),
):
    # 1) generate task id
    task_id = str(uuid.uuid4())

    # 2) create monitor record so client can poll immediately
    task_svc.create(task_id)
    task_svc.progress(task_id, 1)

    # 3) schedule background work (no Celery)
    background.add_task(run_scan_task, task_id, input, task_svc)

    # 4) return task id
    return JSONResponse(content={"task_id": task_id}, status_code=202)


def _normalize_task_payload(task_id: str, state: dict) -> dict:
    payload = dict(state)
    status = payload.get("status")
    if isinstance(status, TaskStatus):
        payload["status"] = status.value
    if "error" not in payload and (
        "error_type" in payload or "error_message" in payload
    ):
        payload["error"] = {
            "error_type": payload.pop("error_type", "UnknownError"),
            "error_message": payload.pop("error_message", "Unknown error"),
        }
    payload["task_id"] = task_id
    return payload


@scanning_router.get(
    "/scan/{task_id}",
    summary="Get scanning task status",
    response_model=TaskStatusResponse,
    tags=["scanning"],
)
def get_scan_task_status(
    task_id: str, task_svc: TaskService = Depends(get_task_service)
):
    state = task_svc.status(task_id)
    return _normalize_task_payload(task_id, state)
