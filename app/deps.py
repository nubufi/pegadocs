# app/deps.py
from functools import lru_cache

from app.application.services.task_service import TaskService
from app.infra.factories.task_stores import TaskStoreFactory


@lru_cache
def _service() -> TaskService:
    factory = TaskStoreFactory()
    store = factory.get_task_store()
    return TaskService(store)


def get_task_service() -> TaskService:
    return _service()
