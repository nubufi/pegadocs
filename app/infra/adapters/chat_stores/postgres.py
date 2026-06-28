from llama_index.core.storage.chat_store.base import BaseChatStore
from llama_index.storage.chat_store.postgres import PostgresChatStore

from app.application.protocols.chat_store_protocol import ChatStoreProtocol


class PostgresCS(ChatStoreProtocol):
    def __init__(self, config: dict, token_limit: int):
        """
        Initialize the PostgresVectorStore with the collection name.

        Args:
            chat_id (str): The ID of the chat session.
            config (dict): Configuration parameters for the vector store. It should inclued the following keys:
                - database: The name of the database.
                - host: The host of the PostgreSQL database.
                - password: The password for the PostgreSQL database.
                - port: The port of the PostgreSQL database.
                - user: The user for the PostgreSQL database.
                - schema: The schema to use in the PostgreSQL database.
                - table_name: The name of the table to use in the PostgreSQL database.
            token_limit (int): The token limit for the chat memory buffer.

        """
        self.config = config
        self.token_limit = token_limit
        self.chat_store = self.get_chat_store()

    def get_chat_store(self) -> BaseChatStore:
        return PostgresChatStore.from_params(
            host=self.config["host"],
            port=str(self.config["port"]),
            database=self.config["database"],
            user=self.config["user"],
            password=self.config["password"],
            schema_name=self.config["schema"],
            table_name=self.config["table_name"],
        )
