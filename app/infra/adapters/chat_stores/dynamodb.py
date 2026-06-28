from llama_index.core.storage.chat_store.base import BaseChatStore
from llama_index.storage.chat_store.dynamodb import DynamoDBChatStore

from app.application.protocols.chat_store_protocol import ChatStoreProtocol


class DynamoDBCS(ChatStoreProtocol):
    def __init__(self, config: dict, token_limit: int):
        """
        Initialize the PostgresVectorStore with the collection name.

        Args:
            config (dict): Configuration parameters for the dynamodb chat store. It should inclued the following keys:
                - table_name: The name of the DynamoDB table.
                - primary_key: The primary key of the DynamoDB table.
                - profile_name: The AWS profile name.
                - region_name: The AWS region name.
                - aws_access_key_id: The AWS access key ID.
                - aws_secret_access_key: The AWS secret access key.
                - aws_session_token: The AWS session token.
            token_limit (int): The token limit for the chat memory buffer.

        """
        self.config = config
        self.token_limit = token_limit
        self.chat_store = self.get_chat_store()

    def get_chat_store(self) -> BaseChatStore:
        table_name = self.config.get("table_name")
        primary_key = self.config.get("primary_key", "SessionId")
        profile_name = self.config.get("profile_name")
        region_name = self.config.get("region_name")
        aws_access_key_id = self.config.get("aws_access_key_id")
        aws_secret_access_key = self.config.get("aws_secret_access_key")
        aws_session_token = self.config.get("aws_session_token")

        if not table_name:
            raise ValueError("DynamoDB table_name must be provided in the config.")

        return DynamoDBChatStore(
            table_name=table_name,
            primary_key=primary_key,
            profile_name=profile_name,
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
        )
