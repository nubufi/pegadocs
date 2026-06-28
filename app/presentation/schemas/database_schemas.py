from typing import Literal
from pydantic import BaseModel


class CreateDataBaseIndexRequest(BaseModel):
    name: str
    type: Literal["postgres", "s3", "chromadb", "pinecone", "dynamodb"]
    config: dict
    storage_type: Literal["vector", "chat"]


class CreateDataBaseIndexResponse(BaseModel):
    id: str


class UpdateDataBaseIndexRequest(BaseModel):
    id: str
    name: str
    type: Literal["postgres", "s3", "chromadb", "pinecone", "dynamodb"]
    config: dict
    storage_type: Literal["vector", "chat"]


class UpdateDataBaseIndexResponse(BaseModel):
    message: str


class ListDataBaseIndexResponse(BaseModel):
    id: str
    name: str
    type: Literal["postgres", "s3", "chromadb", "pinecone", "dynamodb"]
    config: dict
    created_at: str
    is_default: bool = False
    storage_type: Literal["vector", "chat"]


class DeleteDataBaseIndexRequest(BaseModel):
    id: str
