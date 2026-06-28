from typing import Dict, List, Protocol

from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.chat_engine.types import BaseChatEngine, ChatMode
from llama_index.core.llms.utils import LLMType
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.storage.chat_store.base import BaseChatStore

from app.application.models import PricedModel
from app.application.protocols.vector_store_protocol import VectorStoreProtocol


class ChatStoreProtocol(Protocol):
    config: Dict[str, str]
    chat_store: BaseChatStore
    token_limit: int

    def __init__(self, config: Dict[str, str], token_limit: int):
        """
        Initialize the chat store protocol with a chat ID and configuration.

        Args:
            config (Dict[str, str]): Configuration dictionary containing chat store details.
            token_limit (int): The token limit for the chat memory buffer.
            llm_model (LLMType): The language model type to use for the chat.
        """
        self.config = config
        self.token_limit = token_limit
        self.chat_store = self.get_chat_store()

    def get_chat_store(self) -> BaseChatStore:
        """
        Get the chat store for the given configuration.

        Args:
            config (Dict[str, str]): Configuration dictionary containing chat store details.

        Returns:
            BaseChatStore: The chat store instance.
        """
        raise NotImplementedError

    def get_chat_engine(
        self,
        prompt: str,
        vector_store: VectorStoreProtocol,
        priced_llm_model: PricedModel,
        priced_embedding_model: PricedModel,
        chat_id: str,
    ) -> BaseChatEngine:
        """
        Get the chat engine for the given index and chat store key.

        Args:
            prompt (str): Optional system prompt to use for the chat engine.
            vector_store (VectorStoreProtocol): The vector store protocol instance containing the index.
            priced_llm_model (PricedModel): The priced LLM model to use for the chat engine.
            priced_embedding_model (PricedModel): The priced embedding model to use for the chat engine.
        Returns:
            BaseChatEngine: The chat engine configured with the index and memory.
        """

        if not isinstance(priced_embedding_model.model, BaseEmbedding):
            raise ValueError("The model provided is not an embedding model.")
        if not isinstance(priced_llm_model.model, LLMType):
            raise ValueError("The model provided is not a language model.")

        # Create index and chat engine without token counting (token counting happens during chat operations)
        index = vector_store.get_index(
            embedding_model=priced_embedding_model.model,
        )

        chat_engine = index.as_chat_engine(
            chat_mode=ChatMode.CONDENSE_PLUS_CONTEXT,
            memory=self.get_memory(chat_id),
            context_prompt=prompt
            + "\nUse the following context to answer the question. <context>{context_str}</context>",
            verbose=False,
            llm=priced_llm_model.model,
        )

        return chat_engine

    def get_memory(self, chat_id: str) -> ChatMemoryBuffer:
        """
        Get the chat memory buffer for the given chat store and chat ID.

        Args:
            chat_id (str): The unique identifier for the chat session.

        Returns:
            ChatMemoryBuffer: The chat memory buffer instance.
        """
        return ChatMemoryBuffer.from_defaults(
            token_limit=self.token_limit,
            chat_store=self.chat_store,
            chat_store_key=chat_id,
        )

    def get_chat_history(self, chat_id: str) -> List[Dict[str, str]]:
        """
        Fetch the chat history for the given chat ID.

        Args:
            chat_id (str): The unique identifier for the chat session.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing the chat history.
        """
        return [
            {"role": msg.role.value, "message": msg.content or ""}
            for msg in self.get_memory(chat_id).get_all()
        ]

    def delete_chat(self, chat_id) -> None:
        """Delete a chat instance by its ID."""
        self.chat_store.delete_messages(chat_id)
