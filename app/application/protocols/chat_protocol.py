from typing import Generator, Protocol

from app.application.protocols.chat_store_protocol import ChatStoreProtocol
from app.application.protocols.vector_store_protocol import VectorStoreProtocol


class ChatProtocol(Protocol):
    def __init__(
        self,
        vector_store: VectorStoreProtocol,
        chat_store: ChatStoreProtocol,
        chat_id: str,
        system_prompt: str,
    ):
        """Initialize the chat protocol with a chat ID and optional system prompt."""
        raise NotImplementedError

    def stream_chat(self, message: str) -> Generator[str, None, None]:
        """Stream chat responses for the given message."""
        raise NotImplementedError

    def chat(self, message: str) -> str:
        """Send a message to the chat and return the response."""
        raise NotImplementedError
