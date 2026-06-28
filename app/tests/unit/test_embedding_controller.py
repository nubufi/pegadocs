from unittest.mock import MagicMock, patch

import pytest

from app.presentation.controllers.embedding_controller import EmbeddingController
from app.presentation.schemas.embedding_schemas import EmbeddingRequest


@pytest.fixture
def mock_reader_service():
    return MagicMock()


@pytest.fixture
def mock_model_service():
    return MagicMock()


@pytest.fixture
def embedding_controller(mock_reader_service, mock_model_service):
    return EmbeddingController(mock_reader_service, mock_model_service)


@patch(
    "app.presentation.controllers.embedding_controller.get_embedding_model_id_by_collection_id"
)
@patch(
    "app.presentation.controllers.embedding_controller.ReaderMethodFactory.get_reader"
)
def test_embed_documents_success(
    mock_get_reader,
    mock_get_embedding_model_id,
    embedding_controller,
):
    # Arrange
    request = EmbeddingRequest(
        collection_id="ci_asdad",
        data_source_id="ds_456",
        chunk_size=512,
        chunk_overlap=50,
    )

    # Mock the ID fetch
    mock_get_embedding_model_id.return_value = "embedding-model-id"

    # Mock embedder factory
    mock_embedder = MagicMock()
    mock_get_reader.return_value = mock_embedder

    # Act
    embedding_controller.embed_documents(request, "test_user", "job_123")

    # Assert
    mock_get_embedding_model_id.assert_called_once_with("ci_asdad")
    mock_get_reader.assert_called_once_with("ds_456", 512, 50)
    embedding_controller.reader_service.process_documents.assert_called_once_with(
        reader=mock_embedder,
        additional_metadata=request.additional_metadata,
        user_id="test_user",
        job_id="job_123",
    )
