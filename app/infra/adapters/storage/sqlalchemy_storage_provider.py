import json
from datetime import datetime, timezone
from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.adapters.auth.models import LocalMetadata, get_session_local


class SQLAlchemyStorageProvider:
    def _get_session(self) -> Session:
        return get_session_local()()

    def fetch_items(self, table_name: str, col_name: str = "",
                    col_value: Any | None = "", user_id: str = "") -> List[Dict[str, Any]]:
        with self._get_session() as session:
            stmt = select(LocalMetadata).where(LocalMetadata.table_name == table_name)
            if user_id:
                stmt = stmt.where(LocalMetadata.user_id == user_id)
            rows = session.execute(stmt).scalars().all()
            results = []
            for row in rows:
                try:
                    item = json.loads(row.data)
                    if col_name and not col_value:
                        if item.get(col_name) is None:
                            results.append(item)
                    elif col_name and col_value is not None:
                        if item.get(col_name) == col_value:
                            results.append(item)
                    else:
                        results.append(item)
                except (json.JSONDecodeError, TypeError):
                    continue
            return results

    def add_item(self, table_name: str, item_data: dict) -> Any:
        with self._get_session() as session:
            metadata = LocalMetadata(
                table_name=table_name,
                user_id=item_data.get("user_id"),
                data=json.dumps(item_data),
            )
            session.add(metadata)
            session.commit()
            return metadata

    def update_item(self, table_name: str, col_name: str, col_value: str,
                    update_data: dict, user_id: str = "") -> Any:
        with self._get_session() as session:
            stmt = select(LocalMetadata).where(LocalMetadata.table_name == table_name)
            if user_id:
                stmt = stmt.where(LocalMetadata.user_id == user_id)
            rows = session.execute(stmt).scalars().all()

            for row in rows:
                try:
                    item = json.loads(row.data)
                    if item.get(col_name) == col_value:
                        item.update(update_data)
                        row.data = json.dumps(item)
                        row.updated_at = datetime.now(timezone.utc)
                except (json.JSONDecodeError, TypeError):
                    continue
            session.commit()

    def delete_item(self, table_name: str, col_name: str, value: str,
                    user_id: str = "") -> Any:
        with self._get_session() as session:
            stmt = select(LocalMetadata).where(LocalMetadata.table_name == table_name)
            if user_id:
                stmt = stmt.where(LocalMetadata.user_id == user_id)
            rows = session.execute(stmt).scalars().all()

            for row in rows:
                try:
                    item = json.loads(row.data)
                    if item.get(col_name) == value:
                        session.delete(row)
                except (json.JSONDecodeError, TypeError):
                    continue
            session.commit()