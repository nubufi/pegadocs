from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from loguru import logger

from app.application.protocols.chat_store_protocol import ChatStoreProtocol
from app.application.services.chat_service import ChatService
from app.application.services.database_service import DatabaseService
from app.application.services.model_service import ModelService
from app.application.services.prompt_service import PromptService
from app.infra.factories.chat_store import ChatStoreFactory
from app.infra.auth import get_user
from app.infra.config import settings
from app.infra.utils.fastapi_utils import gen_error_response
from app.infra.utils.supabase_utils import fetch_items
from app.infra.utils.vector_store_utils import get_vector_store
from app.presentation.controllers.chat_controller import ChatController
from app.presentation.schemas.chat_schemas import (
    AddChatMetadataRequest,
    AddChatMetadataResponse,
    ChatRequest,
    DeleteChatMetadataResponse,
    FetchChatMetadataResponse,
    GetChatHistoryRequest,
    GetChatHistoryResponse,
    UpdateChatMetadataRequest,
    UpdateChatMetadataResponse,
)


def get_chat_store(
    chat_id: str, user_id: str, token_limit: int = 4096
) -> ChatStoreProtocol:
    """
    Returns a vector store instance for the given collection name.

    Args:
        chat_id (str): The ID of the chat session.
        user_id (str): The ID of the user who owns the collection.
        token_limit (int): The token limit for the chat memory buffer.

    Returns:
        ChatStoreProtocol: An instance of the chat store with the specified chat ID.
    """
    database_service = DatabaseService()
    chat_store = ChatStoreFactory.get_chat_store(
        chat_id, token_limit, database_service, user_id
    )

    return chat_store


def get_chat_controller(
    collection_id: str | None,
    chat_id: str | None,
    user_id: str,
    token_limit: int = 4096,
) -> ChatController:
    """
    Returns a ChatController instance for the given chat ID and user ID.

    Args:
        collection_id (str): The ID of the vector store collection.
        chat_id (str): The ID of the chat session.
        user_id (str): The ID of the user who owns the chat.
        token_limit (int): The token limit for the chat memory buffer.

    Returns:
        ChatController: An instance of the ChatController with the specified chat ID and user ID.
    """
    if collection_id is None:
        metadata = fetch_items(settings.CHAT_HISTORY_TABLE_NAME, "id", chat_id or "")[0]
        collection_id = metadata.get("collection_id")
    if not collection_id:
        raise ValueError("Collection ID not found in chat metadata")
    vector_store = get_vector_store(collection_id, user_id)
    if chat_id is None:
        chat_service = ChatService(vector_store, None)
    else:
        chat_store = get_chat_store(chat_id, user_id, token_limit)
        chat_service = ChatService(vector_store, chat_store)
    model_service = ModelService()
    prompt_service = PromptService()
    return ChatController(chat_service, model_service, prompt_service)


chat_router = APIRouter()


@chat_router.post(
    "/chat",
    summary="Chat with the embedded website",
    tags=["chat"],
    operation_id="chat_with_bot",
)
def chat(input: ChatRequest, user_id=Depends(get_user)):
    try:
        chat_controller = get_chat_controller(
            None, input.chat_id, user_id, input.token_limit
        )
        result = chat_controller.chat(input, user_id)
        return JSONResponse(content=result, status_code=202)
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return gen_error_response(e)


@chat_router.post(
    "/stream-chat",
    summary="Stream chat with the embedded website",
    tags=["chat"],
    operation_id="stream_chat_with_bot",
)
def stream_chat(input: ChatRequest, user_id=Depends(get_user)):
    try:
        chat_controller = get_chat_controller(
            None, input.chat_id, user_id, input.token_limit
        )
        event_stream = chat_controller.stream_chat(input, user_id)
        return StreamingResponse(event_stream, media_type="text/plain")
    except Exception as e:
        logger.error(f"Error in stream chat endpoint: {str(e)}")
        return gen_error_response(e)


@chat_router.post(
    "/add-chat",
    summary="Creates a new chat metadata entry",
    tags=["chat"],
    operation_id="add_chat_metadata",
    response_model=AddChatMetadataResponse,
)
def add_chat(input: AddChatMetadataRequest, user_id=Depends(get_user)):
    try:
        chat_controller = get_chat_controller(input.collection_id, None, user_id)
        result = chat_controller.add_chat(input, user_id)
        return result
    except Exception as e:
        logger.error(f"Error in add chat endpoint: {str(e)}")
        return gen_error_response(e)


@chat_router.delete(
    "/delete-chat/{chat_id}",
    summary="Deletes a chat metadata entry",
    tags=["chat"],
    operation_id="delete_chat_metadata",
    response_model=DeleteChatMetadataResponse,
)
def delete_chat(chat_id: str, user_id=Depends(get_user)):
    try:
        chat_controller = get_chat_controller(None, chat_id, user_id)
        result = chat_controller.delete_chat(chat_id, user_id)
        return result
    except Exception as e:
        logger.error(f"Error in delete chat endpoint: {str(e)}")
        return gen_error_response(e)


@chat_router.get(
    "/list-chats",
    summary="Fetches chat metadata for a specific user",
    tags=["chat"],
    operation_id="list_chat_metadata",
    response_model=List[FetchChatMetadataResponse],
)
def fetch_chats(user_id: str = Depends(get_user)):
    try:
        result = fetch_items(settings.CHAT_HISTORY_TABLE_NAME, "user_id", user_id)
        if not result:
            raise HTTPException(status_code=404, detail="No chats found for the user")
        return result
    except Exception as e:
        logger.error(f"Error in fetch chats endpoint: {str(e)}")
        return gen_error_response(e)


@chat_router.post(
    "/get-chat-history",
    summary="Fetches chat history for a specific chat ID",
    tags=["chat"],
    operation_id="get_chat_history",
    response_model=List[GetChatHistoryResponse],
)
def get_chat_history(input: GetChatHistoryRequest, user_id=Depends(get_user)):
    try:
        chat_controller = get_chat_controller(None, input.chat_id, user_id)
        result = chat_controller.get_chat_history(input, user_id)

        return result
    except Exception as e:
        logger.error(f"Error in get chat history endpoint: {str(e)}")
        return gen_error_response(e)


@chat_router.post(
    "/update-chat",
    summary="Updates a chat metadata entry",
    tags=["chat"],
    operation_id="update_chat_metadata",
    response_model=UpdateChatMetadataResponse,
)
def update_chat(input: UpdateChatMetadataRequest, user_id=Depends(get_user)):
    try:
        chat_controller = get_chat_controller(input.collection_id, None, user_id, 0)
        result = chat_controller.update_chat(input, user_id)
        return result
    except Exception as e:
        logger.error(f"Error in add chat endpoint: {str(e)}")
        return gen_error_response(e)
