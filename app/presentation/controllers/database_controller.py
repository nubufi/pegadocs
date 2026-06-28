from typing import List, Dict
from app.infra.utils.encrypt_utils import decrypt_dict
from app.application.services.database_service import DatabaseService
from app.presentation.schemas.database_schemas import (
    CreateDataBaseIndexRequest,
    CreateDataBaseIndexResponse,
    ListDataBaseIndexResponse,
    UpdateDataBaseIndexRequest,
    UpdateDataBaseIndexResponse,
)


class DataBaseController:
    """Controller for database index operations"""

    def __init__(self, database_service: DatabaseService):
        self.database_service = database_service

    def create_database_index(
        self, request: CreateDataBaseIndexRequest, user_id: str
    ) -> CreateDataBaseIndexResponse:
        """
        Handle database index creation request

        Args:
            request (CreateDataBaseIndexRequest): The request object containing database index details.
            user_id (str): The ID of the user creating the index.
        Returns:
            CreateDataBaseIndexResponse: The response object containing the ID of the created database index.
        """
        db_id = self.database_service.create_database_index(
            user_id=user_id,
            db_name=request.name,
            db_type=request.type,
            config=request.config,
            storage_type=request.storage_type,
        )
        return CreateDataBaseIndexResponse(id=db_id)

    def update_database_index(
        self, request: UpdateDataBaseIndexRequest, user_id: str
    ) -> UpdateDataBaseIndexResponse:
        """
        Handle database index update request
        Args:
            request (UpdateDataBaseIndexRequest): The request object containing updated database index details.
            user_id (str): The ID of the user updating the index.
        Returns:
            UpdateDataBaseIndexResponse: The response object indicating the success of the update operation.
        """
        self.database_service.update_database_index(
            user_id=user_id,
            db_id=request.id,
            db_name=request.name,
            db_type=request.type,
            config=request.config,
            storage_type=request.storage_type,
        )
        return UpdateDataBaseIndexResponse(
            message="Database index updated successfully"
        )

    def list_database_indexes(self, user_id: str) -> List[ListDataBaseIndexResponse]:
        """
        Handle database index listing request

        Args:
            user_id (str): The ID of the user whose database indexes are to be listed.
        Returns:
            List[ListDataBaseIndexResponse]: A list of database index response objects.
        """
        indexes = self.database_service.list_database_indexes(user_id)
        return [
            ListDataBaseIndexResponse(
                id=index["id"],
                name=index["name"],
                type=index["type"],
                config=decrypt_dict(index["config"]) if index["config"] else {},
                created_at=index["created_at"],
                is_default=index["is_default"],
                storage_type=index["storage_type"],
            )
            for index in indexes
        ]

    def delete_database_index(self, db_id: str, user_id: str) -> Dict[str, str]:
        """
        Handle database index deletion request

        Args:
            db_id (str): The ID of the database index to be deleted.
            user_id (str): The ID of the user requesting the deletion.
        Returns:
            Dict[str, str]: A message indicating the success of the deletion operation.
        """
        self.database_service.delete_database_index(db_id, user_id)
        return {"message": "Database index deleted successfully"}
