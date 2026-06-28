from app.application.protocols.chat_store_protocol import ChatStoreProtocol
from app.application.services.database_service import DatabaseService
from app.infra.config import settings
from app.infra.utils.encrypt_utils import decrypt_dict
from app.infra.utils.supabase_utils import fetch_items
from app.infra.adapters.chat_stores.dynamodb import DynamoDBCS
from app.infra.adapters.chat_stores.postgres import PostgresCS
from app.infra.adapters.chat_stores.redis import RedisCS


class ChatStoreFactory:
    @staticmethod
    def get_chat_store(
        chat_id: str,
        token_limit: int,
        database_service: DatabaseService,
        user_id: str,
    ) -> ChatStoreProtocol:
        """
        Factory method to create a chat store instance.

        Args:
            chat_id (str): The ID of the chat session.
            token_limit (int): The token limit for the chat memory buffer.
            database_service (DatabaseService): An instance of the database service to fetch database index.
            user_id (str): The ID of the user to fetch the database index for.

        Returns:
            ChatStoreProtocol: An instance of a chat store protocol.
        """
        resp = fetch_items(settings.CHAT_HISTORY_TABLE_NAME, "id", chat_id)
        if not resp:
            raise ValueError(f"Chat with ID {chat_id} does not exist.")

        db_id = resp[0].get("database_id")
        if not db_id:
            raise ValueError(f"Chat with ID {chat_id} does not have a database ID.")

        database_index = database_service.get_database_index(db_id, user_id)
        if not database_index:
            raise ValueError(
                f"Database with ID {db_id} does not exist for user {user_id}."
            )

        database_config = decrypt_dict(database_index["config"])
        if not database_config:
            raise ValueError(
                f"Database configuration for ID {db_id} is empty or invalid."
            )
        database_type = database_index.get("type", "")

        if database_type == "postgres":
            return PostgresCS(database_config, token_limit)
        elif database_type == "redis":
            return RedisCS(database_config, token_limit)
        elif database_type == "dynamodb":
            return DynamoDBCS(database_config, token_limit)
        else:
            raise ValueError(f"Unsupported database type: {database_type}")
