from typing import Any, Dict, List
from dotenv import load_dotenv

from app.infra.config import settings

load_dotenv()

_supabase = None


def _get_supabase():
    global _supabase
    if _supabase is None:
        from supabase import create_client

        _supabase = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY
        )
    return _supabase


def delete_item(table_name: str, col_name: str, value: str, user_id: str = ""):
    if user_id:
        return (
            _get_supabase().table(table_name)
            .delete()
            .eq(col_name, value)
            .eq("user_id", user_id)
            .execute()
        )
    return _get_supabase().table(table_name).delete().eq(col_name, value).execute()


def add_item(table_name: str, item_data: dict):
    return _get_supabase().table(table_name).insert(item_data).execute()


def update_item(
    table_name: str, col_name: str, col_value: str, update_data: dict, user_id: str = ""
):
    if user_id:
        return (
            _get_supabase().table(table_name)
            .update(update_data)
            .eq(col_name, col_value)
            .eq("user_id", user_id)
            .execute()
        )
    return (
        _get_supabase().table(table_name).update(update_data).eq(col_name, col_value).execute()
    )


def fetch_items(
    table_name: str, col_name: str = "", col_value: Any | None = "", user_id: str = ""
) -> List[Dict[str, Any]]:
    query = _get_supabase().table(table_name).select("*")

    if col_name and col_value is None:
        query = query.is_(col_name, None)
    elif col_name and col_value:
        query = query.eq(col_name, col_value)

    if user_id:
        query = query.eq("user_id", user_id)

    response = query.execute()
    return response.data