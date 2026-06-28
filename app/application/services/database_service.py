from typing import Any, Dict, List
from loguru import logger

from app.application.exceptions import (
    DatabaseIndexCreationException,
    DatabaseIndexDeletionException,
    DatabaseIndexListException,
    DatabaseIndexNotFoundException,
    DatabaseIndexUpdateException,
    OperationFailedException,
)
from app.infra.config import settings
from app.infra.utils.encrypt_utils import encrypt_dict
from app.infra.utils.supabase_utils import (
    add_item,
    delete_item,
    fetch_items,
    update_item,
)


class DatabaseService:
    """Service for database operations related to database operations"""

    table_name = settings.DATABASE_TABLE_NAME

    def get_default_database_indexes(self) -> List[Dict[str, str]]:
        logger.info(f"Fetching default database index from table: {self.table_name}")
        try:
            response = fetch_items(self.table_name, "is_default", True)
            if response:
                logger.debug("Default database index found.")
                for r in response:
                    r["config"] = {}
                return response
            logger.warning("No default database index found.")
            return []
        except Exception as e:
            logger.exception("Failed to get default database index")
            raise OperationFailedException(
                f"Failed to get default database index: {str(e)}"
            )

    def create_database_index(
        self,
        user_id: str,
        db_name: str,
        db_type: str,
        config: dict,
        storage_type: str,
    ) -> str:
        logger.info(f"Creating database index '{db_name}' for user_id={user_id}")
        try:
            encrypted_config = encrypt_dict(config)
            response = add_item(
                self.table_name,
                {
                    "user_id": user_id,
                    "name": db_name,
                    "type": db_type,
                    "storage_type": storage_type,
                    "config": encrypted_config,
                },
            )
            db_id = response.data[0]["id"] if response.data else ""
            logger.debug(f"Database index created with ID: {db_id}")
            return db_id
        except Exception as e:
            logger.exception("Failed to create database index")
            raise DatabaseIndexCreationException(
                f"Failed to generate database index: {str(e)}"
            )

    def update_database_index(
        self,
        user_id: str,
        db_id: str,
        db_name: str,
        db_type: str,
        config: dict,
        storage_type: str,
    ) -> str:
        logger.info(f"Updating database index '{db_name}' for db_id={db_id}")
        try:
            encrypted_config = encrypt_dict(config)
            update_item(
                self.table_name,
                "id",
                db_id,
                {
                    "name": db_name,
                    "type": db_type,
                    "storage_type": storage_type,
                    "config": encrypted_config,
                },
                user_id,
            )
            logger.debug(f"Database index updated with ID: {db_id}")
            return db_id
        except Exception as e:
            logger.exception("Failed to update database index")
            raise DatabaseIndexUpdateException(
                f"Failed to update database index: {str(e)}"
            )

    def list_database_indexes(self, user_id: str) -> List[Dict[str, Any]]:
        logger.info(f"Listing database indexes for user_id={user_id}")
        try:
            default_index = self.get_default_database_indexes()
            response = fetch_items(self.table_name, "user_id", user_id)
            user_indexes = response if response else []
            logger.debug(f"Found {len(user_indexes)} user-specific indexes.")
            result = default_index + user_indexes if default_index else user_indexes
            logger.debug(f"Total returned indexes: {len(result)}")
            return result
        except Exception as e:
            logger.exception("Failed to list database indexes")
            raise DatabaseIndexListException(
                f"Failed to list database indexes: {str(e)}"
            )

    def delete_database_index(self, db_id: str, user_id: str) -> None:
        logger.info(f"Attempting to delete database index with ID: {db_id}")
        try:
            response = delete_item(self.table_name, "id", db_id, user_id)
            if not response.data:
                logger.warning(f"Database index {db_id} not found.")
                raise DatabaseIndexNotFoundException(
                    f"Database index {db_id} not found."
                )
            logger.debug(f"Database index {db_id} successfully deleted.")
        except Exception as e:
            logger.exception("Failed to delete database index")
            raise DatabaseIndexDeletionException(
                f"Failed to delete database index: {str(e)}"
            )

    def check_if_db_is_default(self, db_id: str) -> bool:
        logger.info(f"Checking if database index with ID: {db_id} is default")
        try:
            response = fetch_items(self.table_name, "id", db_id)
            if not response:
                logger.warning(f"Database index {db_id} not found.")
                raise DatabaseIndexNotFoundException(
                    f"Database index {db_id} not found."
                )
            is_default = response[0].get("is_default", False)
            logger.debug(f"Database index {db_id} is_default={is_default}")
            return is_default
        except Exception as e:
            logger.exception("Failed to check if database index is default")
            raise DatabaseIndexNotFoundException(
                f"Failed to check if database index is default: {str(e)}"
            )

    def get_database_index(self, db_id: str, user_id: str) -> dict:
        logger.info(f"Fetching database index with ID: {db_id} for user_id={user_id}")
        try:
            is_default = self.check_if_db_is_default(db_id)
            if is_default:
                user_id = None
            response = fetch_items(self.table_name, "id", db_id, user_id)
            if not response:
                logger.warning(f"Database index {db_id} not found.")
                raise DatabaseIndexNotFoundException(
                    f"Database index {db_id} not found."
                )
            logger.debug(f"Database index {db_id} retrieved successfully.")
            return response[0]
        except Exception as e:
            logger.exception("Failed to retrieve database index")
            raise DatabaseIndexNotFoundException(
                f"Failed to get database index: {str(e)}"
            )
