# app/tasks/scanning_bg.py
from typing import List
import logging

from app.application.services.reader_service import ReaderService
from app.presentation.controllers.scanning_controller import ScanningController
from app.presentation.schemas.scanning_schemas import ScanningRequest
from app.application.services.task_service import TaskService

logger = logging.getLogger(__name__)


def run_scan_task(task_id: str, req: ScanningRequest, task_svc: TaskService) -> None:
    """Blocking worker executed by FastAPI BackgroundTasks."""
    try:
        # idempotent create + early progress
        task_svc.create(task_id)
        task_svc.progress(task_id, 1)

        reader_service = ReaderService()
        controller = ScanningController(reader_service)

        task_svc.progress(task_id, 10)

        documents: List[str] = controller.scan(request=req)

        task_svc.complete(task_id, {"documents": documents})
    except Exception as exc:
        logger.exception("Scanning background task failed")
        task_svc.fail(task_id, exc.__class__.__name__, str(exc))
