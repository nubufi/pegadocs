from app.infra.config import settings
from app.infra.utils.supabase_utils import add_item, delete_item, fetch_items


def add_chat_metadata(
    collection_id: str,
    user_id: str,
    chat_name: str,
    database_id: str,
    model_id: str,
    chat_source: str,
    prompt_id: str,
    table_name: str = settings.CHAT_HISTORY_TABLE_NAME,
) -> str:
    """
    Adds chat metadata to the specified collection.

    Args:
        collection_id (str): The ID of the collection to which the chat metadata will be added.
        user_id (str): The ID of the user adding the chat metadata.
        chat_name (str): The name of the chat.
        database_id (str): The ID of the database to which the chat belongs.
        model_id (str): The ID of the model used for the chat.
        chat_source (str): The source of the chat (e.g., "user", "system").
        prompt_id (str): The ID of the prompt associated with the chat.
        table_name (str): The name of the table where the chat metadata will be stored. Defaults to CHAT_TABLE.

    Returns:
        str: The ID of the newly created chat metadata entry, or None if the operation fails.
    """
    response = add_item(
        table_name,
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
        return response.data[0]["id"]

    raise ValueError("Failed to add chat metadata: No data returned from Supabase.")


def delete_chat_metadata(
    chat_id: str, table_name: str = settings.CHAT_HISTORY_TABLE_NAME
):
    """
    Deletes chat metadata from the specified table.

    Args:
        chat_id (str): The ID of the chat metadata to delete.
        table_name (str): The name of the table from which to delete the chat metadata. Defaults to settings.CHAT_HISTORY_TABLE_NAME.
    """
    return delete_item(table_name, "id", chat_id)


def list_chat_metadata(
    user_id: str, table_name: str = settings.CHAT_HISTORY_TABLE_NAME
) -> list:
    """
    Fetches chat metadata for a specific user.

    Args:
        user_id (str): The ID of the user whose chat metadata is to be fetched.
        table_name (str): The name of the table from which to fetch the chat metadata. Defaults to settings.CHAT_HISTORY_TABLE_NAME.

    Returns:
        list: A list of chat metadata entries for the specified user.
    """
    return fetch_items(table_name, "user_id", user_id)


def get_chat_metadata(
    chat_id: str, table_name: str = settings.CHAT_HISTORY_TABLE_NAME
) -> dict:
    """
    Fetches chat metadata for a specific user.

    Args:
        chat_id (str): The ID of the chat metadata to fetch.
        table_name (str): The name of the table from which to fetch the chat metadata. Defaults to settings.CHAT_HISTORY_TABLE_NAME.

    Returns:
        dict: The chat metadata entry for the specified chat ID.

    """
    return fetch_items(table_name, "id", chat_id)[0]
