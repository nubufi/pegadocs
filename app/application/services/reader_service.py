from typing import Any, Dict

from loguru import logger

from app.application.exceptions import EmbeddingException
from app.application.protocols.reader_protocol import ReaderProtocol


class ReaderService:
    """Business logic for document embedding operations"""

    def process_documents(
        self,
        reader: ReaderProtocol,
        additional_metadata: Dict[str, Any],
        user_id: str,
        job_id: str,
    ):
        """
        Process the embedding operation using the specified embedding method.
        """
        logger.info("Starting document embedding process...")
        try:
            reader.process(
                additional_metadata=additional_metadata,
                job_id=job_id,
            )
        except Exception as e:
            logger.exception("Embedding operation failed")
            raise EmbeddingException(f"Embedding operation failed: {str(e)}")
