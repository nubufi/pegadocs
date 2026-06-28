from pydantic import BaseModel


class CreatePromptRequest(BaseModel):
    name: str
    prompt: str


class CreatePromptResponse(BaseModel):
    id: str


class UpdatePromptRequest(BaseModel):
    name: str
    prompt: str
    id: str


class UpdatePromptResponse(BaseModel):
    message: str


class DeletePromptRequest(BaseModel):
    id: str


class ListPromptsResponse(BaseModel):
    id: str
    name: str
    prompt: str
