from typing import Any, Dict
from pydantic import BaseModel

from app.infra.config import settings


class EmbeddingRequest(BaseModel):
    data_source_id: str
    collection_id: str
    chunk_size: int = settings.CHUNK_SIZE
    chunk_overlap: int = settings.CHUNK_OVERLAP
    additional_metadata: Dict[str, Any] = {}
