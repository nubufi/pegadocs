# tasks/backends/redis_store.py
from __future__ import annotations
import json, time
from typing import Any
import boto3
from botocore.exceptions import ClientError
from app.application.protocols.task_store import TaskState, TaskStore, TaskStatus
from loguru import logger


class DynamoDBTaskStore(TaskStore):
    """
    Table schema (recommended):
      - PK: task_id (S)
      - status (S)   one of PROCESSING/DONE/ERROR
      - progress (N)
      - created_at (N, epoch seconds)
      - updated_at (N, epoch seconds)
      - result (S, JSON)          only for DONE
      - error_type (S), error_message (S) only for ERROR
      - expires_at (N, epoch seconds)     (enable TTL on this attribute)
    """

    def __init__(
        self,
        table_name: str,
        region_name: str,
        ttl_seconds: int = 3 * 24 * 3600,
        boto3_session: boto3.session.Session | None = None,
    ) -> None:
        session = boto3_session or boto3.session.Session(region_name=region_name)
        self.table = session.resource("dynamodb").Table(table_name)
        self.ttl = ttl_seconds

    def init_task(self, task_id: str) -> bool:
        now = int(time.time())
        item = {
            "task_id": task_id,
            "status": TaskStatus.PROCESSING.value,
            "progress": 0,
            "created_at": now,
            "updated_at": now,
            "expires_at": now + self.ttl,
        }
        try:
            self.table.put_item(
                Item=item, ConditionExpression="attribute_not_exists(task_id)"
            )
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] in ("ConditionalCheckFailedException",):
                return False
            raise

    def set_progress(self, task_id: str, progress: int) -> None:
        now = int(time.time())
        self.table.update_item(
            Key={"task_id": task_id},
            UpdateExpression="SET progress=:p, updated_at=:u, expires_at=:e",
            ExpressionAttributeValues={":p": progress, ":u": now, ":e": now + self.ttl},
        )

    def _finish(self, task_id: str, status: TaskStatus, extra: dict) -> bool:
        now = int(time.time())

        # Base attributes we always update
        base_updates = {
            "status": status.value,
            "updated_at": now,
            "expires_at": now + self.ttl,
        }

        # Merge with extras (e.g., result/progress or error_* fields)
        all_updates = {**base_updates, **extra}

        # Build expression parts with name aliases for safety
        names = {}
        values = {}
        set_parts = []

        for k, v in all_updates.items():
            name_key = f"#n_{k}"  # e.g. #n_result
            value_key = f":v_{k}"  # e.g. :v_result
            names[name_key] = k  # map alias -> real attribute
            values[value_key] = v
            set_parts.append(f"{name_key} = {value_key}")

        update_expr = "SET " + ", ".join(set_parts)

        # Condition: only transition from PROCESSING
        names["#n_status"] = "status"  # ensure included, even if not in extras
        values[":v_processing"] = TaskStatus.PROCESSING

        try:
            self.table.update_item(
                Key={"task_id": task_id},
                UpdateExpression=update_expr,
                ExpressionAttributeNames={**names},
                ExpressionAttributeValues={**values},
                ConditionExpression="#n_status = :v_processing",
            )
            return True
        except ClientError as e:
            logger.error(f"DynamoDBTaskStore _finish error: {e}")
            if e.response["Error"]["Code"] in (
                "ConditionalCheckFailedException",
                "ValidationException",
                "ResourceNotFoundException",
            ):
                return False
            raise

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
        res = self.table.get_item(Key={"task_id": task_id})
        item = res.get("Item")
        if not item:
            return {"status": TaskStatus.UNKNOWN}

        status = TaskStatus(item.get("status", TaskStatus.UNKNOWN))
        base = {
            "status": status,
            "progress": int(item.get("progress", 0)),
            "created_at": int(item.get("created_at", 0)),
            "updated_at": int(item.get("updated_at", 0)),
        }

        if status == TaskStatus.DONE:
            result_raw = item.get("result")
            try:
                result = (
                    json.loads(result_raw)
                    if isinstance(result_raw, str)
                    else result_raw
                )
            except Exception:
                result = {"raw": result_raw}
            return {**base, "result": result}
        if status == TaskStatus.ERROR:
            return {
                **base,
                "error_type": item.get("error_type", "UnknownError"),
                "error_message": item.get("error_message", "Unknown error"),
            }
        return base  # PROCESSING
