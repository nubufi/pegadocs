from typing import List, Dict, Tuple

from app.application.models import PricedModel
from app.application.services.chat_service import ChatService
from app.application.services.model_service import ModelService
from app.application.services.prompt_service import PromptService
from app.infra.factories.models import ModelFactory
from app.infra.utils.collection_utils import get_embedding_model_id_by_collection_id
from app.presentation.schemas.chat_schemas import (
    ChatRequest,
    AddChatMetadataRequest,
    GetChatHistoryRequest,
    AddChatMetadataResponse,
    DeleteChatMetadataResponse,
    FetchChatMetadataResponse,
    GetChatHistoryResponse,
    UpdateChatMetadataRequest,
    UpdateChatMetadataResponse,
)


class ChatController:
    """Controller for chat operations"""

    def __init__(
        self,
        chat_service: ChatService,
        model_service: ModelService,
        prompt_service: PromptService,
    ):
        self.chat_service = chat_service
        self.model_service = model_service
        self.prompt_service = prompt_service

    def get_models(
        self, model_id: str, collection_id: str
    ) -> Tuple[PricedModel, PricedModel]:
        llm_model = ModelFactory(self.model_service).get_llm_model(model_id)

        embedding_model_id = get_embedding_model_id_by_collection_id(collection_id)
        if not embedding_model_id:
            raise ValueError(
                "Embedding model ID not found for the given collection ID."
            )
        embedding_model = ModelFactory(self.model_service).get_embedding_model(
            embedding_model_id
        )

        return embedding_model, llm_model

    def get_system_prompt(self, prompt_id: str) -> str:
        prompt_data = self.prompt_service.get_prompt(prompt_id)
        prompt = prompt_data.get("prompt")
        if not prompt:
            raise ValueError("Prompt not found for the given prompt ID")
        return prompt

    def chat_kwargs(self, request: ChatRequest, user_id) -> Dict:
        metadata = self.chat_service.get_chat_metadata(request.chat_id, user_id)
        model_id = metadata.get("model_id")
        collection_id = metadata.get("collection_id")
        prompt_id = metadata.get("prompt_id")
        if not model_id:
            raise ValueError("Model ID not found in chat metadata")

        if not collection_id:
            raise ValueError("Collection ID not found in chat metadata")

        if not prompt_id:
            raise NotImplementedError("Prompt ID not found in chat metadata")

        prompt = self.get_system_prompt(prompt_id)

        embedding_model, llm_model = self.get_models(model_id, collection_id)

        return {
            "collection_id": collection_id,
            "chat_id": request.chat_id,
            "message": request.message,
            "system_prompt": prompt,
            "llm_model": llm_model,
            "embedding_model": embedding_model,
            "user_id": user_id,
        }

    def chat(self, request: ChatRequest, user_id: str) -> Dict[str, str]:
        """
        Handle chat request

        Args:
            request (ChatRequest): The chat request containing collection_id, chat_id, message, and system_prompt
        Returns:
            Dict[str, str]: The response from the chat service
        """
        response = self.chat_service.chat(**self.chat_kwargs(request, user_id))
        return {"response": response}

    def stream_chat(self, request: ChatRequest, user_id: str):
        """
        Handle stream chat request

        Args:
            request (ChatRequest): The chat request containing collection_id, chat_id, message, and system_prompt
        Returns:
            Streaming response from the chat service
        """
        return self.chat_service.stream_chat(**self.chat_kwargs(request, user_id))

    def add_chat(
        self, request: AddChatMetadataRequest, user_id: str
    ) -> AddChatMetadataResponse:
        """
        Handle add chat request

        Args:
            request (AddChatMetadataRequest): The request containing collection_id and chat_name
            user_id (str): The ID of the user adding the chat
        Returns:
            AddChatMetadataResponse: The response containing the chat ID of the newly created chat
        """
        chat_id = self.chat_service.add_chat(
            collection_id=request.collection_id,
            user_id=user_id,
            chat_name=request.chat_name,
            database_id=request.database_id,
            model_id=request.model_id,
            chat_source=request.chat_source,
            prompt_id=request.prompt_id,
        )
        return AddChatMetadataResponse(chat_id=chat_id)

    def update_chat(
        self, request: UpdateChatMetadataRequest, user_id: str
    ) -> UpdateChatMetadataResponse:
        """
        Handle update chat ChatRequest
        Args:
            request (UpdateChatMetadataRequest): The request containing chat_id, collection_id, and chat_name
        Returns:
            UpdateChatMetadataResponse: The response indicating the chat was updated successfully
        """
        self.chat_service.update_chat(
            chat_id=request.chat_id,
            collection_id=request.collection_id,
            chat_name=request.chat_name,
            database_id=request.database_id,
            model_id=request.model_id,
            chat_source=request.chat_source,
            prompt_id=request.prompt_id,
            user_id=user_id,
        )

        return UpdateChatMetadataResponse(
            message=f"Chat with ID {request.chat_id} updated successfully"
        )

    def delete_chat(self, chat_id: str, user_id: str) -> DeleteChatMetadataResponse:
        """Handle delete chat request"""
        self.chat_service.delete_chat(user_id, chat_id)
        return DeleteChatMetadataResponse(
            message=f"Chat with ID {chat_id} deleted successfully"
        )

    def get_chats(self, user_id: str) -> List[FetchChatMetadataResponse]:
        """
        Handle get chats request

        Args:
            user_id (str): The ID of the user whose chats are being fetched
        Returns:
            List[FetchChatMetadataResponse]: A list of chat metadata responses
        """
        chats = self.chat_service.get_chats(user_id)
        return [
            FetchChatMetadataResponse(
                id=chat["id"],
                collection_id=chat["collection_id"],
                name=chat["name"],
                created_at=chat["created_at"],
                model_id=chat["model_id"],
                chat_source=chat["chat_source"],
                prompt_id=chat["prompt_id"],
            )
            for chat in chats
        ]

    def get_chat_history(
        self, request: GetChatHistoryRequest, user_id: str
    ) -> List[GetChatHistoryResponse]:
        """
        Handle get chat history request

        Args:
            request (GetChatHistoryRequest): The request containing collection_id and chat_id
        Returns:
            List[GetChatHistoryResponse]: A list of chat history responses
        """
        metadata = self.chat_service.get_chat_metadata(request.chat_id, user_id)
        collection_id = metadata.get("collection_id")
        if not collection_id:
            raise ValueError("Collection ID not found in chat metadata")

        history = self.chat_service.get_chat_history(
            collection_id=collection_id, chat_id=request.chat_id
        )
        return [
            GetChatHistoryResponse(role=chat["role"], message=chat["message"])
            for chat in history
        ]
