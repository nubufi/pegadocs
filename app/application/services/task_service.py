# tasks/service.py
from __future__ import annotations
from typing import Any

from app.application.protocols.task_store import TaskState, TaskStore


class TaskService:
    def __init__(self, store: TaskStore) -> None:
        self.store = store

    def create(self, task_id: str) -> bool:
        return self.store.init_task(task_id)

    def progress(self, task_id: str, progress: int) -> None:
        self.store.set_progress(task_id, max(0, min(100, progress)))

    def complete(self, task_id: str, result: dict) -> bool:
        return self.store.set_result(task_id, result)

    def fail(self, task_id: str, err_type: str, err_msg: str, **extras: Any) -> bool:
        return self.store.set_error(task_id, err_type, err_msg, **extras)

    def status(self, task_id: str) -> TaskState:
        return self.store.get_result(task_id)
