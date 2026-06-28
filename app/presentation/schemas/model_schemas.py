from typing import Dict, Literal, Optional
from pydantic import BaseModel


class CreateModelRequest(BaseModel):
    name: str
    type: Literal["chat", "embedding"]
    dimensions: Optional[int] = None
    provider: Literal["azure_openai"]
    config: Dict[str, str]


class CreateModelResponse(BaseModel):
    id: str


class UpdateModelRequest(BaseModel):
    id: str
    name: str
    type: Literal["chat", "embedding"]
    dimensions: Optional[int] = None
    provider: Literal["azure_openai"]
    config: Dict[str, str]


class UpdateModelResponse(BaseModel):
    message: str


class DeleteModelRequest(BaseModel):
    id: str


class ListModelsResponse(BaseModel):
    id: str
    name: str
    provider: Literal["azure_openai"]
    type: Literal["chat", "embedding"]
    is_default: Optional[bool] = False
    dimensions: Optional[int] = None
    config: Dict[str, str]
    input_price_per_1k_token: Optional[float] = None
    output_price_per_1k_token: Optional[float] = None
