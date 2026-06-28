from unittest.mock import Mock

import pytest

from app.application.exceptions import EmbeddingException
from app.application.services.reader_service import ReaderService


class TestReaderService:
    def setup_method(self):
        self.reader_service = ReaderService()

    def test_embed_content_calls_embedding_method(self):
        mock_reader = Mock()

        self.reader_service.process_documents(
            reader=mock_reader,
            additional_metadata={},
            user_id="test_user",
            job_id="job_123",
        )

        mock_reader.process.assert_called_once_with(
            additional_metadata={},
            job_id="job_123",
        )

    def test_embed_content_failure(self):
        mock_reader = Mock()

        mock_reader.process.side_effect = Exception("embedding error")

        with pytest.raises(
            EmbeddingException, match="Embedding operation failed: embedding error"
        ):
            self.reader_service.process_documents(
                reader=mock_reader,
                additional_metadata={},
                user_id="test_user",
                job_id="job_123",
            )
