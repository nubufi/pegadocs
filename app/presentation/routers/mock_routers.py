"""Opt-in, in-memory auth and chat API for client development."""

from datetime import datetime, timezone
from threading import RLock
from typing import Annotated, Iterator
from uuid import uuid4

from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.presentation.schemas.auth_schemas import (
    AuthResponse,
    LoginRequest,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RegisterRequest,
    RegisterResponse,
)
from app.presentation.schemas.chat_schemas import (
    AddChatMetadataRequest,
    AddChatMetadataResponse,
    ChatRequest,
    DeleteChatMetadataResponse,
    FetchChatMetadataResponse,
    GetChatHistoryRequest,
    GetChatHistoryResponse,
)

mock_router = APIRouter(tags=["mock"])


class MockChatResponse(BaseModel):
    response: str


class _MockState:
    def __init__(self) -> None:
        self.lock = RLock()
        self.users: dict[str, dict[str, str]] = {
            "demo@pegadocs.local": {
                "user_id": "mock-user-demo",
                "password": "demo1234",
                "name": "Demo User",
            }
        }
        self.tokens: dict[str, str] = {}
        self.refresh_tokens: dict[str, str] = {}
        self.chats: dict[str, dict[str, str]] = {}
        self.history: dict[str, list[dict[str, str]]] = {}

    def issue_tokens(self, user_id: str) -> tuple[str, str]:
        access_token = f"mock-access-{uuid4()}"
        refresh_token = f"mock-refresh-{uuid4()}"
        self.tokens[access_token] = user_id
        self.refresh_tokens[refresh_token] = user_id
        return access_token, refresh_token


_state = _MockState()


def _get_mock_user_id(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    scheme, _, token = (authorization or "").partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mock bearer token required",
        )
    with _state.lock:
        user_id = _state.tokens.get(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid mock bearer token",
        )
    return user_id


def _owned_chat(chat_id: str, user_id: str) -> dict[str, str]:
    chat = _state.chats.get(chat_id)
    if not chat or chat["user_id"] != user_id:
        raise HTTPException(status_code=404, detail="Mock chat not found")
    return chat


@mock_router.post("/auth/register", response_model=RegisterResponse, status_code=201)
def mock_register(request: RegisterRequest) -> RegisterResponse:
    with _state.lock:
        if request.email in _state.users:
            raise HTTPException(
                status_code=409, detail="Email address is already in use"
            )
        user_id = f"mock-user-{uuid4()}"
        _state.users[request.email] = {
            "user_id": user_id,
            "password": request.password,
            "name": request.name,
        }
    return RegisterResponse(user_id=user_id, email=request.email)


@mock_router.post("/auth/login", response_model=AuthResponse)
def mock_login(request: LoginRequest) -> AuthResponse:
    with _state.lock:
        user = _state.users.get(request.email)
        if not user or user["password"] != request.password:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        access_token, refresh_token = _state.issue_tokens(user["user_id"])
    return AuthResponse(
        user_id=user["user_id"],
        email=request.email,
        name=user["name"],
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=3600,
    )


@mock_router.post("/auth/refresh", response_model=RefreshTokenResponse)
def mock_refresh(request: RefreshTokenRequest) -> RefreshTokenResponse:
    with _state.lock:
        user_id = _state.refresh_tokens.pop(request.refresh_token, None)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid mock refresh token")
        access_token, refresh_token = _state.issue_tokens(user_id)
    return RefreshTokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=3600,
    )


@mock_router.post("/add-chat", response_model=AddChatMetadataResponse)
def mock_add_chat(
    request: AddChatMetadataRequest,
    authorization: Annotated[str | None, Header()] = None,
) -> AddChatMetadataResponse:
    user_id = _get_mock_user_id(authorization)
    chat_id = f"mock-chat-{uuid4()}"
    with _state.lock:
        _state.chats[chat_id] = {
            "id": chat_id,
            "user_id": user_id,
            "collection_id": request.collection_id,
            "name": request.chat_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "model_id": request.model_id,
            "prompt_id": request.prompt_id,
            "chat_source": request.chat_source,
        }
        _state.history[chat_id] = []
    return AddChatMetadataResponse(chat_id=chat_id)


@mock_router.post("/chat", response_model=MockChatResponse, status_code=202)
def mock_chat(
    request: ChatRequest,
    authorization: Annotated[str | None, Header()] = None,
) -> MockChatResponse:
    user_id = _get_mock_user_id(authorization)
    response = f"Mock response to: {request.message}"
    with _state.lock:
        _owned_chat(request.chat_id, user_id)
        _state.history[request.chat_id].extend(
            [
                {"role": "user", "message": request.message},
                {"role": "assistant", "message": response},
            ]
        )
    return MockChatResponse(response=response)


@mock_router.post("/stream-chat")
def mock_stream_chat(
    request: ChatRequest,
    authorization: Annotated[str | None, Header()] = None,
) -> StreamingResponse:
    response = mock_chat(request, authorization).response

    def chunks() -> Iterator[str]:
        for word in response.split():
            yield f"{word} "

    return StreamingResponse(chunks(), media_type="text/plain")


@mock_router.get("/list-chats", response_model=list[FetchChatMetadataResponse])
def mock_list_chats(
    authorization: Annotated[str | None, Header()] = None,
) -> list[FetchChatMetadataResponse]:
    user_id = _get_mock_user_id(authorization)
    with _state.lock:
        chats = [
            chat.copy()
            for chat in _state.chats.values()
            if chat["user_id"] == user_id
        ]
    return [FetchChatMetadataResponse.model_validate(chat) for chat in chats]


@mock_router.post(
    "/get-chat-history", response_model=list[GetChatHistoryResponse]
)
def mock_get_chat_history(
    request: GetChatHistoryRequest,
    authorization: Annotated[str | None, Header()] = None,
) -> list[GetChatHistoryResponse]:
    user_id = _get_mock_user_id(authorization)
    with _state.lock:
        _owned_chat(request.chat_id, user_id)
        history = list(_state.history[request.chat_id])
    return [GetChatHistoryResponse.model_validate(message) for message in history]


@mock_router.delete(
    "/delete-chat/{chat_id}", response_model=DeleteChatMetadataResponse
)
def mock_delete_chat(
    chat_id: str,
    authorization: Annotated[str | None, Header()] = None,
) -> DeleteChatMetadataResponse:
    user_id = _get_mock_user_id(authorization)
    with _state.lock:
        _owned_chat(chat_id, user_id)
        del _state.chats[chat_id]
        del _state.history[chat_id]
    return DeleteChatMetadataResponse(
        message=f"Chat with ID {chat_id} deleted successfully"
    )
