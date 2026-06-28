from llama_index.core.storage.chat_store.base import BaseChatStore
from llama_index.storage.chat_store.redis import RedisChatStore

from app.application.protocols.chat_store_protocol import ChatStoreProtocol


class RedisCS(ChatStoreProtocol):
    def __init__(self, config: dict, token_limit: int):
        """
        Initialize the PostgresVectorStore with the collection name.

        Args:
            config (dict): Configuration parameters for the vector store. It should inclued the following keys:
                - host: The host of the PostgreSQL database.
                - port: The port of the PostgreSQL database.
            token_limit (int): The token limit for the chat memory buffer.

        """
        self.config = config
        self.token_limit = token_limit
        self.chat_store = self.get_chat_store()

    def get_chat_store(self) -> BaseChatStore:
        host = self.config["host"]
        port = self.config["port"]

        if not host or not port:
            raise ValueError("Redis host and port must be provided in the config.")

        url = f"redis://{host}:{port}"

        return RedisChatStore(redis_url=url)
