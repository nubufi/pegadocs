# tasks/backends/redis_store.py
from __future__ import annotations
import json, time
from typing import Any
from redis import Redis
from app.application.protocols.task_store import TaskState, TaskStore, TaskStatus

_TASK_PREFIX = "tasks:"


class RedisTaskStore(TaskStore):
    def __init__(self, client: Redis, ttl_seconds: int = 3 * 24 * 3600) -> None:
        # Tip: construct Redis with decode_responses=True
        self.r = client
        self.ttl = ttl_seconds

    def _k(self, task_id: str) -> str:
        return f"{_TASK_PREFIX}{task_id}"

    def init_task(self, task_id: str) -> bool:
        k = self._k(task_id)
        # Only create if doesn't exist
        pipe = self.r.pipeline()
        while True:
            try:
                pipe.watch(k)
                if self.r.exists(k):
                    pipe.unwatch()
                    return False
                pipe.multi()
                now = int(time.time())
                pipe.hset(
                    k,
                    mapping={
                        "status": TaskStatus.PROCESSING.value,
                        "progress": 0,
                        "created_at": now,
                        "updated_at": now,
                    },
                )
                pipe.expire(k, self.ttl)
                pipe.execute()
                return True
            finally:
                pipe.reset()

    def set_progress(self, task_id: str, progress: int) -> None:
        k = self._k(task_id)
        if self.r.exists(k):
            self.r.hset(
                k, mapping={"progress": progress, "updated_at": int(time.time())}
            )
            self.r.expire(k, self.ttl)

    def _finish(self, task_id: str, status: TaskStatus, extra: dict) -> bool:
        k = self._k(task_id)
        pipe = self.r.pipeline()
        while True:
            try:
                pipe.watch(k)
                if not self.r.exists(k):
                    pipe.unwatch()
                    return False
                current = self.r.hget(k, "status")
                if current != TaskStatus.PROCESSING.value:
                    pipe.unwatch()
                    return False
                pipe.multi()
                update = {"status": status.value, "updated_at": int(time.time())}
                update.update(extra)
                pipe.hset(k, mapping=update)
                pipe.expire(k, self.ttl)
                pipe.execute()
                return True
            finally:
                pipe.reset()

    def set_result(self, task_id: str, result: dict) -> bool:
        return self._finish(
            task_id,
            TaskStatus.DONE,
            {"result": json.dumps(result, default=str), "progress": 100},
        )

    def set_error(
        self, task_id: str, error_type: str, error_message: str, **kwargs: Any
    ) -> bool:
        payload = {"error_type": error_type, "error_message": error_message}
        payload.update({k: str(v) for k, v in kwargs.items()})
        return self._finish(task_id, TaskStatus.ERROR, payload)

    def get_result(self, task_id: str) -> TaskState:
        k = self._k(task_id)
        if not self.r.exists(k):
            return {"status": TaskStatus.UNKNOWN}

        data = self.r.hgetall(k)
        status = TaskStatus(data.get("status", TaskStatus.UNKNOWN))
        base = {
            "status": status,
            "progress": int(data.get("progress", 0)),
            "created_at": int(data.get("created_at", 0)),
            "updated_at": int(data.get("updated_at", 0)),
        }

        if status == TaskStatus.DONE:
            try:
                result = json.loads(data.get("result", "{}"))
            except Exception:
                result = {"raw": data.get("result")}
            return {**base, "result": result}
        if status == TaskStatus.ERROR:
            return {
                **base,
                "error_type": data.get("error_type", "UnknownError"),
                "error_message": data.get("error_message", "Unknown error"),
            }
        return base  # PROCESSING
