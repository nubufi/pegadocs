from unittest.mock import MagicMock, patch

import pytest
from llama_index.core import Document

from app.application.exceptions import OperationFailedException
from app.infra.config import settings
from app.infra.utils import embedding_job_utils as job_utils


@patch("app.infra.utils.embedding_job_utils.boto3")
def test_persist_documents_for_job_uploads_and_records(mock_boto3, monkeypatch):
    mock_s3_client = MagicMock()
    mock_table = MagicMock()
    mock_dynamodb_resource = MagicMock()
    mock_dynamodb_resource.Table.return_value = mock_table

    mock_boto3.client.return_value = mock_s3_client
    mock_boto3.resource.return_value = mock_dynamodb_resource

    monkeypatch.setattr(settings, "S3_DATA_SOURCE_BUCKET_NAME", "test-bucket")
    monkeypatch.setattr(settings, "S3_EMBEDDING_BUCKET_NAME", "test-embed-bucket")
    monkeypatch.setattr(settings, "JOB_STATUS_TABLE_NAME", "job-status")

    doc = Document(text="hello world", doc_id="doc-1")

    folder_name = job_utils.persist_documents_for_job(
        documents=[doc],
        job_id="job-456",
        chunk_overlap=5,
        chunk_size=50,
    )

    assert folder_name == "job-456"
    mock_s3_client.upload_file.assert_called_once()
    mock_table.put_item.assert_called_once()


def test_record_job_status_without_job_id(monkeypatch):
    monkeypatch.setattr(settings, "JOB_STATUS_TABLE_NAME", "job-status")
    with pytest.raises(OperationFailedException):
        job_utils.record_job_status(
            job_id="",
            chunk_overlap=5,
            chunk_size=50,
        )


def test_upload_documents_to_s3_missing_bucket(monkeypatch):
    monkeypatch.setattr(settings, "S3_EMBEDDING_BUCKET_NAME", "")
    with pytest.raises(OperationFailedException):
        job_utils.upload_documents_to_s3("job", [])
