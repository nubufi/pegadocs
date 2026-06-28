# tasks/backends/redis_store.py
from __future__ import annotations
from redis import Redis
from app.infra.config import settings
from app.application.protocols.task_store import TaskStore
from app.infra.adapters.task_stores.dynamodb import DynamoDBTaskStore
from app.infra.adapters.task_stores.redis import RedisTaskStore


class TaskStoreFactory:
    @staticmethod
    def get_task_store() -> TaskStore:
        if settings.TASK_STORE.lower() == "redis":
            client = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
            )
            return RedisTaskStore(client=client, ttl_seconds=settings.TTL_SECONDS)

        if settings.TASK_STORE.lower() == "dynamodb":
            return DynamoDBTaskStore(
                table_name=settings.DDB_TABLE,
                region_name=settings.AWS_REGION,
                ttl_seconds=settings.TTL_SECONDS,
            )

        raise ValueError(f"Unsupported TASK_STORE: {settings.TASK_STORE}")
