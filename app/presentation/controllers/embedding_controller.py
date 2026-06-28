from app.application.services.reader_service import ReaderService
from app.application.services.model_service import ModelService
from app.infra.factories.reader import ReaderMethodFactory
from app.infra.utils.collection_utils import get_embedding_model_id_by_collection_id
from app.presentation.schemas.embedding_schemas import EmbeddingRequest


class EmbeddingController:
    """Controller for embedding operations"""

    def __init__(
        self,
        reader_service: ReaderService,
        model_service: ModelService,
    ):
        self.reader_service = reader_service
        self.model_service = model_service

    def embed_documents(
        self,
        request: EmbeddingRequest,
        user_id: str,
        job_id: str,
    ):
        """Handle website embedding request (backward compatibility)"""
        embedding_model_id = get_embedding_model_id_by_collection_id(
            request.collection_id
        )
        if not embedding_model_id:
            raise ValueError(
                "Embedding model ID not found for the given collection ID."
            )
        reader = ReaderMethodFactory.get_reader(
            request.data_source_id, request.chunk_size, request.chunk_overlap
        )
        self.reader_service.process_documents(
            reader=reader,
            additional_metadata=request.additional_metadata,
            user_id=user_id,
            job_id=job_id,
        )
