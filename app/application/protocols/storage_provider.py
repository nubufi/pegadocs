from typing import Any, Dict, List, Protocol, runtime_checkable


@runtime_checkable
class StorageProviderProtocol(Protocol):
    def fetch_items(self, table_name: str, col_name: str = "",
                    col_value: Any | None = "", user_id: str = "") -> List[Dict[str, Any]]:
        ...

    def add_item(self, table_name: str, item_data: dict) -> Any:
        ...

    def update_item(self, table_name: str, col_name: str, col_value: str,
                    update_data: dict, user_id: str = "") -> Any:
        ...

    def delete_item(self, table_name: str, col_name: str, value: str,
                    user_id: str = "") -> Any:
        ...