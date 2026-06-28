from typing import Literal
from pydantic import BaseModel


class ChatRequest(BaseModel):
    chat_id: str
    message: str
    token_limit: int = 4096


class GetChatHistoryRequest(BaseModel):
    chat_id: str


class GetChatHistoryResponse(BaseModel):
    role: str
    message: str


class AddChatMetadataRequest(BaseModel):
    database_id: str
    collection_id: str
    chat_name: str
    chat_source: Literal["web", "mobile", "desktop", "telegram", "whatsapp", "teams"]
    model_id: str
    prompt_id: str


class AddChatMetadataResponse(BaseModel):
    chat_id: str


class UpdateChatMetadataRequest(BaseModel):
    chat_id: str
    database_id: str
    collection_id: str
    chat_name: str
    chat_source: Literal["web", "mobile", "desktop", "telegram", "whatsapp", "teams"]
    model_id: str
    prompt_id: str


class UpdateChatMetadataResponse(BaseModel):
    message: str


class DeleteChatMetadataResponse(BaseModel):
    message: str


class FetchChatMetadataResponse(BaseModel):
    id: str
    collection_id: str
    name: str
    created_at: str
    model_id: str
    prompt_id: str
    chat_source: Literal["web", "mobile", "desktop", "telegram", "whatsapp", "teams"]
