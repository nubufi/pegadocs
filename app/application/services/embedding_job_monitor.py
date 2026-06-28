from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional

import boto3
from boto3.dynamodb.conditions import Key

from app.infra.config import settings

_dynamodb = boto3.resource("dynamodb", region_name=settings.AWS_REGION)
_file_status_table = _dynamodb.Table(settings.FILE_STATUS_TABLE_NAME)
_nodes_table = _dynamodb.Table(settings.NODES_TABLE_NAME)


def _to_int(value: Optional[int | float | Decimal]) -> int:
    if value is None:
        return 0
    if isinstance(value, Decimal):
        return int(value)
    return int(value)


def _query_all_items(table, job_id: str) -> List[dict]:
    items: List[dict] = []
    key_expression = Key("job_id").eq(job_id)
    response = table.query(KeyConditionExpression=key_expression)
    items.extend(response.get("Items", []))
    while "LastEvaluatedKey" in response:
        response = table.query(
            KeyConditionExpression=key_expression,
            ExclusiveStartKey=response["LastEvaluatedKey"],
        )
        items.extend(response.get("Items", []))
    return items


@dataclass
class JobSyncSummary:
    job_id: str
    expected_counts: Dict[str, int]
    actual_counts: Dict[str, int]
    total_tokens: int
    total_expected_nodes: int
    total_actual_nodes: int
    data_source_id: Optional[str]
    failed_nodes_count: int = 0

    @property
    def ready(self) -> bool:
        if self.total_expected_nodes <= 0:
            return False
        expected_docs = set(self.expected_counts.keys())
        actual_docs = set(self.actual_counts.keys())
        if expected_docs != actual_docs:
            return False
        return all(
            self.actual_counts.get(doc_id, 0) == expected
            for doc_id, expected in self.expected_counts.items()
        )

    @property
    def pending_documents(self) -> Dict[str, Dict[str, int]]:
        details: Dict[str, Dict[str, int]] = {}
        for doc_id, expected in self.expected_counts.items():
            actual = self.actual_counts.get(doc_id, 0)
            if actual != expected:
                details[doc_id] = {"expected": expected, "actual": actual}
        for doc_id, actual in self.actual_counts.items():
            if doc_id not in self.expected_counts:
                details[doc_id] = {"expected": 0, "actual": actual}
        return details

    @property
    def progress_percent(self) -> int:
        if self.total_expected_nodes <= 0:
            return 0
        progress = int(
            min(
                100,
                (self.total_actual_nodes / self.total_expected_nodes) * 100,
            )
        )
        return max(progress, 0)

    @property
    def failure_rate(self) -> float:
        if self.total_actual_nodes <= 0:
            return 0.0
        return self.failed_nodes_count / self.total_actual_nodes


class EmbeddingJobMonitor:
    def load_summary(self, job_id: str) -> JobSyncSummary:
        file_items = _query_all_items(_file_status_table, job_id)
        expected_counts: Dict[str, int] = {}
        expected_total = 0
        for item in file_items:
            doc_id = item.get("doc_id")
            if not doc_id:
                continue
            count = _to_int(item.get("number_of_nodes", 0))
            expected_counts[doc_id] = count
            expected_total += count

        node_items = _query_all_items(_nodes_table, job_id)
        actual_counts: Dict[str, int] = defaultdict(int)
        total_tokens = 0
        actual_total = 0
        failed_nodes_count = 0
        data_source_ids = set()

        for node in node_items:
            doc_id = node.get("doc_id")
            if doc_id:
                actual_counts[doc_id] += 1
                actual_total += 1
            total_tokens += _to_int(node.get("token_size", 0))
            data_source_id = node.get("data_source_id")
            if data_source_id:
                data_source_ids.add(data_source_id)
            
            if node.get("status") == "failed":
                failed_nodes_count += 1

        data_source_id = None
        if len(data_source_ids) == 1:
            data_source_id = next(iter(data_source_ids))
        elif len(data_source_ids) > 1:
            raise ValueError(
                f"Multiple data_source_ids found for job {job_id}: {data_source_ids}"
            )

        return JobSyncSummary(
            job_id=job_id,
            expected_counts=expected_counts,
            actual_counts=dict(actual_counts),
            total_tokens=total_tokens,
            total_expected_nodes=expected_total,
            total_actual_nodes=actual_total,
            data_source_id=data_source_id,
            failed_nodes_count=failed_nodes_count,
        )
