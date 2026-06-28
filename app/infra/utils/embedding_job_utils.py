import os
import json
import re
import tempfile
import time
from pathlib import Path
from typing import Dict, Sequence

import boto3
from botocore.exceptions import ClientError
from loguru import logger
from llama_index.core.schema import Document

from app.application.exceptions import OperationFailedException
from app.infra.config import settings

_SAFE_FILENAME_PATTERN = re.compile(r"[^0-9A-Za-z._-]+")
_ONE_DAY_SECONDS = 24 * 3600


def _get_s3_client():
    return boto3.client("s3", region_name=settings.AWS_REGION)


def _get_job_status_table():
    dynamodb = boto3.resource("dynamodb", region_name=settings.AWS_REGION)
    return dynamodb.Table(settings.JOB_STATUS_TABLE_NAME)


def _json_default(value):
    return str(value)


def _sanitize_identifier(value: str | None) -> str | None:
    if not value:
        return None
    sanitized = _SAFE_FILENAME_PATTERN.sub("_", value).strip("._")
    return sanitized or None


def _build_file_name(document: Document, job_id: str | None, index: int) -> str:
    base_name = _sanitize_identifier(document.doc_id) or f"document_{index}"
    prefix = f"{_sanitize_identifier(job_id)}_" if job_id else ""
    return f"{prefix}{base_name}.json"


def _get_expiration_timestamp() -> int:
    return int(time.time()) + _ONE_DAY_SECONDS


def upload_documents_to_s3(
    job_id: str,
    documents: Sequence[Document],
) -> str:
    bucket_name = settings.S3_EMBEDDING_BUCKET_NAME
    if not bucket_name:
        raise OperationFailedException("S3 bucket name is not configured.")

    if not job_id:
        raise OperationFailedException("job_id is required to upload documents.")

    folder_name = _sanitize_identifier(job_id) or job_id or "job"
    folder_prefix = f"{folder_name}/"
    s3_client = _get_s3_client()
    uploaded_files = 0

    with tempfile.TemporaryDirectory() as tmp_dir:
        target_dir = Path(tmp_dir) / folder_name
        target_dir.mkdir(parents=True, exist_ok=True)

        for index, document in enumerate(documents, start=1):
            file_name = _build_file_name(document, job_id, index)
            file_path = target_dir / file_name
            file_path.write_text(
                json.dumps(
                    document.to_json(), ensure_ascii=False, default=_json_default
                ),
                encoding="utf-8",
            )
            s3_key = f"{folder_prefix}{file_name}"
            try:
                s3_client.upload_file(str(file_path), bucket_name, s3_key)
            except ClientError as exc:
                logger.exception(
                    "Failed to upload %s for job %s to bucket %s",
                    s3_key,
                    job_id,
                    bucket_name,
                )
                raise OperationFailedException(
                    "Unable to upload documents to S3."
                ) from exc
            uploaded_files += 1
            try:
                os.remove(file_path)
            except:
                pass

    if uploaded_files == 0:
        try:
            s3_client.put_object(Bucket=bucket_name, Key=folder_prefix)
        except ClientError as exc:
            logger.exception(
                "Failed to create placeholder folder %s in bucket %s",
                folder_prefix,
                bucket_name,
            )
            raise OperationFailedException(
                "Unable to create folder placeholder in S3."
            ) from exc

    return folder_name


def record_job_status(
    job_id: str,
    chunk_size: int,
    chunk_overlap: int,
) -> None:
    if not job_id:
        raise OperationFailedException("job_id is required to record job status.")

    table_name = settings.JOB_STATUS_TABLE_NAME
    if not table_name:
        raise OperationFailedException("JOB_STATUS_TABLE_NAME is not configured.")

    table = _get_job_status_table()
    item = {
        "job_id": str(job_id),
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "expired_at": _get_expiration_timestamp(),
    }

    try:
        table.put_item(Item=item)
    except ClientError as exc:
        logger.exception("Failed to record job status for job %s", job_id)
        raise OperationFailedException("Unable to record job status.") from exc


def persist_documents_for_job(
    documents: Sequence[Document],
    job_id: str,
    chunk_size: int,
    chunk_overlap: int,
) -> str:
    record_job_status(job_id, chunk_size, chunk_overlap)
    folder_name = upload_documents_to_s3(job_id, documents)
    return folder_name
