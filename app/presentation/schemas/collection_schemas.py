from typing import Literal

from pydantic import BaseModel


class CreateCollectionRequest(BaseModel):
    collection_name: str
    database_id: str
    embedding_model_id: str


class CreateCollectionResponse(BaseModel):
    collection_id: str
    collection_name: str


class ListCollectionsResponse(BaseModel):
    id: str
    user_id: str
    name: str
    created_at: str
