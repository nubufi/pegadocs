# tasks/domain.py
from __future__ import annotations
from enum import StrEnum
from typing import Protocol, runtime_checkable, Any, TypedDict


class TaskStatus(StrEnum):
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class TaskSuccess(TypedDict, total=False):
    status: TaskStatus  # DONE
    result: dict
    progress: int
    created_at: int
    updated_at: int


class TaskProcessing(TypedDict, total=False):
    status: TaskStatus  # PROCESSING
    progress: int
    created_at: int
    updated_at: int


class TaskError(TypedDict, total=False):
    status: TaskStatus  # ERROR
    error_type: str
    error_message: str
    progress: int
    created_at: int
    updated_at: int


class TaskUnknown(TypedDict):
    status: TaskStatus  # UNKNOWN


TaskState = TaskSuccess | TaskProcessing | TaskError | TaskUnknown


@runtime_checkable
class TaskStore(Protocol):
    """Storage-agnostic interface for task tracking."""

    def init_task(self, task_id: str) -> bool: ...
    def set_progress(self, task_id: str, progress: int) -> None: ...
    def set_result(self, task_id: str, result: dict) -> bool: ...
    def set_error(
        self, task_id: str, error_type: str, error_message: str, **kwargs: Any
    ) -> bool: ...
    def get_result(self, task_id: str) -> TaskState: ...
