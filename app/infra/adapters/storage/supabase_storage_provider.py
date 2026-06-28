from typing import Any, Dict, List

from app.infra.utils.supabase_utils import add_item as sb_add
from app.infra.utils.supabase_utils import delete_item as sb_delete
from app.infra.utils.supabase_utils import fetch_items as sb_fetch
from app.infra.utils.supabase_utils import update_item as sb_update


class SupabaseStorageProvider:
    def fetch_items(self, table_name: str, col_name: str = "",
                    col_value: Any | None = "", user_id: str = "") -> List[Dict[str, Any]]:
        return sb_fetch(table_name, col_name, col_value, user_id)

    def add_item(self, table_name: str, item_data: dict) -> Any:
        return sb_add(table_name, item_data)

    def update_item(self, table_name: str, col_name: str, col_value: str,
                    update_data: dict, user_id: str = "") -> Any:
        return sb_update(table_name, col_name, col_value, update_data, user_id)

    def delete_item(self, table_name: str, col_name: str, value: str,
                    user_id: str = "") -> Any:
        return sb_delete(table_name, col_name, value, user_id)