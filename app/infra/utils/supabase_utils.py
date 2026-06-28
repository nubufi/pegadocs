from typing import Any, Dict, List
from dotenv import load_dotenv

from app.infra.config import settings

load_dotenv()
from supabase import Client, create_client

supabase: Client = create_client(
    settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY
)


def delete_item(table_name: str, col_name: str, value: str, user_id: str = ""):
    """
    Deletes an item from a specified table in Supabase.

    Args:
        table_name (str): The name of the table from which to delete the item.
        col_name (str): The column name to match the item ID.
        value (str): The value to match in the specified column for deletion.
    """
    if user_id:
        return (
            supabase.table(table_name)
            .delete()
            .eq(col_name, value)
            .eq("user_id", user_id)
            .execute()
        )
    return supabase.table(table_name).delete().eq(col_name, value).execute()


def add_item(table_name: str, item_data: dict):
    """
    Adds an item to a specified table in Supabase.

    Args:
        table_name (str): The name of the table to insert the item into.
        item_data (dict): A dictionary representing the item to insert.
                          Keys are column names and values are the values to insert.
    """
    return supabase.table(table_name).insert(item_data).execute()


def update_item(
    table_name: str, col_name: str, col_value: str, update_data: dict, user_id: str = ""
):
    """
    Updates an item in a specified table in Supabase.

    Args:
        table_name (str): The name of the table to update the item in.
        col_name (str): The column name to match the item ID.
        col_value (str): The value to match in the specified column for updating.
        update_data (dict): A dictionary representing the updated data.
                            Keys are column names and values are the new values to set.
    """
    if user_id:
        return (
            supabase.table(table_name)
            .update(update_data)
            .eq(col_name, col_value)
            .eq("user_id", user_id)
            .execute()
        )
    return (
        supabase.table(table_name).update(update_data).eq(col_name, col_value).execute()
    )


def fetch_items(
    table_name: str, col_name: str = "", col_value: Any | None = "", user_id: str = ""
) -> List[Dict[str, Any]]:
    """
    Fetches items from a specified table in Supabase.

    Args:
        table_name (str): The name of the table to fetch from.
        col_name (str, optional): Column name to filter by.
        col_value (str, optional): Value to match in the filter.
        user_id (str, optional): User ID to filter by.
    Returns:
        list: A list of rows (dictionaries) returned from Supabase.
    """
    query = supabase.table(table_name).select("*")

    if col_name and col_value is None:
        query = query.is_(col_name, None)
    elif col_name and col_value:
        query = query.eq(col_name, col_value)

    if user_id:
        query = query.eq("user_id", user_id)

    response = query.execute()
    return response.data
