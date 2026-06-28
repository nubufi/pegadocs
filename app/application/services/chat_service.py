from typing import Any, Dict, List

from llama_index.core.chat_engine.types import BaseChatEngine
from loguru import logger

from app.application.exceptions import (
    ChatDeleteException,
    ChatFailedException,
    ChatMetadataAddException,
    ChatMetadataFetchException,
    ChatNotFoundException,
    CollectionNotFoundException,
)
from app.application.models import PricedModel
from app.application.protocols.chat_store_protocol import ChatStoreProtocol
from app.application.protocols.vector_store_protocol import VectorStoreProtocol
from app.application.services.database_service import DatabaseService
from app.infra.config import settings
from app.infra.factories.chat_store import ChatStoreFactory
from app.infra.utils.supabase_utils import (
    add_item,
    delete_item,
    fetch_items,
    update_item,
)
from app.infra.utils.token_counter import token_counter_context


class ChatService:
    """Business logic for chat operations"""

    table_name = settings.CHAT_HISTORY_TABLE_NAME

    def __init__(
        self,
        vector_store: VectorStoreProtocol,
        chat_store: ChatStoreProtocol | None,
    ):
        self.vector_store = vector_store
        self.chat_store = chat_store

    def _get_chat_engine(
        self,
        llm_model: PricedModel,
        embedding_model: PricedModel,
        system_prompt: str,
        user_id: str,
        chat_id: str,
    ) -> BaseChatEngine:
        if not self.chat_store:
            logger.error("Chat store is not initialized.")
            raise ChatFailedException("Chat store is not initialized.")

        return self.chat_store.get_chat_engine(
            system_prompt,
            self.vector_store,
            llm_model,
            embedding_model,
            chat_id,
        )

    def chat(
        self,
        collection_id: str,
        chat_id: str,
        message: str,
        llm_model: PricedModel,
        embedding_model: PricedModel,
        system_prompt: str,
        user_id: str,
    ) -> str:
        logger.info(
            f"Chat request received for chat_id={chat_id}, collection_id={collection_id}"
        )
        if not self.vector_store.check_collection():
            logger.warning(f"Collection {collection_id} does not exist")
            raise CollectionNotFoundException(
                f"Either Collection {collection_id} does not exist or it is empty."
            )

        if not self.chat_store:
            logger.error("Chat store is not initialized.")
            raise ChatFailedException("Chat store is not initialized.")

        try:
            chat_engine = self._get_chat_engine(
                system_prompt=system_prompt,
                llm_model=llm_model,
                embedding_model=embedding_model,
                user_id=user_id,
                chat_id=chat_id,
            )
            # Use token counter context for chat operations
            with token_counter_context(
                user_id=user_id,
                embedding_model=embedding_model,
                llm_model=llm_model,
            ) as token_counter:
                # Set callback manager on chat engine for token counting
                chat_engine.callback_manager = token_counter.callback_manager

                response = chat_engine.chat(message)
                return response.response
        except Exception as e:
            logger.exception(f"Failed to process chat message: {e}")
            raise ChatFailedException(f"Failed to process chat message: {str(e)}")

    def stream_chat(
        self,
        collection_id: str,
        chat_id: str,
        message: str,
        llm_model: PricedModel,
        embedding_model: PricedModel,
        system_prompt: str,
        user_id: str,
    ):
        logger.info(
            f"Streaming chat for chat_id={chat_id}, collection_id={collection_id}"
        )
        if not self.vector_store.check_collection():
            logger.warning(f"Collection {collection_id} does not exist")
            raise CollectionNotFoundException(
                f"Collection {collection_id} does not exist."
            )

        if not self.chat_store:
            logger.error("Chat store is not initialized.")
            raise ChatFailedException("Chat store is not initialized.")

        try:
            chat_engine = self._get_chat_engine(
                system_prompt=system_prompt,
                llm_model=llm_model,
                embedding_model=embedding_model,
                user_id=user_id,
                chat_id=chat_id,
            )
            # Use token counter context for chat operations
            with token_counter_context(
                user_id=user_id,
                embedding_model=embedding_model,
                llm_model=llm_model,
            ) as token_counter:
                # Set callback manager on chat engine for token counting
                chat_engine.callback_manager = token_counter.callback_manager

                response = chat_engine.stream_chat(message)
                return response.response_gen
        except Exception as e:
            logger.exception(f"Failed to stream chat messages: {e}")
            raise ChatFailedException(f"Failed to stream chat messages: {str(e)}")

    def add_chat(
        self,
        collection_id: str,
        user_id: str,
        chat_name: str,
        database_id: str,
        model_id: str,
        chat_source: str,
        prompt_id: str,
    ) -> str:
        logger.info(
            f"Adding chat metadata for user_id={user_id}, chat_name={chat_name}, collection_id={collection_id}"
        )
        try:
            response = add_item(
                self.table_name,
                {
                    "collection_id": collection_id,
                    "user_id": user_id,
                    "name": chat_name,
                    "database_id": database_id,
                    "model_id": model_id,
                    "chat_source": chat_source,
                    "prompt_id": prompt_id,
                },
            )
            if response and response.data:
                chat_id = response.data[0]["id"]
                logger.debug(f"Chat metadata added successfully with chat_id={chat_id}")
                return chat_id
            raise ChatMetadataAddException(
                "Failed to add chat metadata: No data returned from Supabase."
            )
        except Exception as e:
            logger.exception(f"Failed to add chat metadata: {e}")
            raise ChatMetadataAddException(f"Failed to add chat metadata: {str(e)}")

    def update_chat(
        self,
        chat_id: str,
        collection_id: str,
        user_id: str,
        chat_name: str,
        database_id: str,
        model_id: str,
        chat_source: str,
        prompt_id: str,
    ) -> str:
        logger.info(f"Updating chat metadata for user_id={user_id}, chat_id={chat_id}")
        try:
            response = update_item(
                self.table_name,
                "id",
                chat_id,
                {
                    "collection_id": collection_id,
                    "user_id": user_id,
                    "name": chat_name,
                    "database_id": database_id,
                    "model_id": model_id,
                    "chat_source": chat_source,
                    "prompt_id": prompt_id,
                },
                user_id,
            )
            if response and response.data:
                chat_id = response.data[0]["id"]
                logger.debug(
                    f"Chat metadata updated successfully with chat_id={chat_id}"
                )
                return chat_id
            raise ChatMetadataAddException(
                "Failed to add chat metadata: No data returned from Supabase."
            )
        except Exception as e:
            logger.exception(f"Failed to add chat metadata: {e}")
            raise ChatMetadataAddException(f"Failed to add chat metadata: {str(e)}")

    def _initialize_chat_store(self, chat_id: str, user_id: str) -> ChatStoreProtocol:
        database_service = DatabaseService()
        chat_store = ChatStoreFactory.get_chat_store(
            chat_id, 100, database_service, user_id
        )
        return chat_store

    def delete_chat(self, user_id: str, chat_id: str) -> None:
        logger.info("Attempting to delete chat.")
        chat_store = self.chat_store or self._initialize_chat_store(chat_id, user_id)
        try:
            chat_store.delete_chat(chat_id)
            delete_item(self.table_name, "id", chat_id, user_id)
            logger.debug("Chat deleted successfully.")
        except Exception as e:
            logger.exception(f"Failed to delete chat: {e}")
            raise ChatDeleteException(f"Failed to delete chat: {str(e)}")

    def get_chats(self, user_id: str) -> List[Dict[str, Any]]:
        logger.info(f"Fetching chat metadata for user_id={user_id}")
        try:
            metadata = fetch_items(self.table_name, "user_id", user_id)
            logger.debug(f"{len(metadata)} chat(s) found for user_id={user_id}")
            return metadata
        except Exception as e:
            logger.exception(f"Failed to fetch chat metadata: {e}")
            raise ChatMetadataFetchException(f"Failed to fetch chat metadata: {str(e)}")

    def get_chat_history(
        self, collection_id: str, chat_id: str
    ) -> List[Dict[str, Any]]:
        chat_store = self.chat_store or self._initialize_chat_store(chat_id, "")
        logger.info(
            f"Retrieving chat history for chat_id={chat_id}, collection_id={collection_id}"
        )
        if not self.vector_store.check_collection():
            logger.warning(f"Collection {collection_id} does not exist")
            raise CollectionNotFoundException(
                f"Collection {collection_id} does not exist."
            )

        try:
            history = chat_store.get_chat_history(chat_id)
            logger.debug(
                f"{len(history)} history messages retrieved for chat_id={chat_id}"
            )
            return history
        except Exception as e:
            logger.exception(f"Chat {chat_id} not found: {e}")
            raise ChatNotFoundException(f"Chat {chat_id} not found: {str(e)}")

    def get_chat_metadata(self, chat_id: str, user_id: str) -> Dict[str, Any]:
        logger.info(f"Fetching metadata for chat_id={chat_id}")
        try:
            items = fetch_items(self.table_name, "id", chat_id, user_id)
            if not items:
                logger.warning(f"Chat metadata with ID {chat_id} not found.")
                raise ChatNotFoundException(
                    f"Chat metadata with ID {chat_id} not found."
                )
            logger.debug(f"Chat metadata retrieved successfully for chat_id={chat_id}")
            return items[0]
        except Exception as e:
            logger.exception(f"Failed to fetch chat metadata: {e}")
            raise ChatMetadataFetchException(f"Failed to fetch chat metadata: {str(e)}")

    def delete_chats_by_collection(self, collection_id: str, user_id: str) -> None:
        logger.info(f"Deleting chats for collection ID: {collection_id}")
        try:
            chats = fetch_items(self.table_name, "collection_id", collection_id)
            for chat in chats:
                self.delete_chat(user_id, chat["id"])
            logger.debug(
                f"All chats for collection ID {collection_id} deleted successfully."
            )
        except Exception as e:
            logger.exception(
                f"Failed to delete chats for collection {collection_id}: {e}"
            )
            raise ChatDeleteException(f"Failed to delete chats: {str(e)}")
