from typing import Dict, List
from app.application.services.model_service import ModelService
from app.presentation.schemas.model_schemas import (
    CreateModelRequest,
    CreateModelResponse,
    ListModelsResponse,
    UpdateModelRequest,
    UpdateModelResponse,
)


class ModelController:
    """Controller for database index operations"""

    def __init__(self, model_service: ModelService):
        self.model_service = model_service

    def create_model(
        self, request: CreateModelRequest, user_id: str
    ) -> CreateModelResponse:
        """
        Handle database index creation request

        Args:
            request (CreateModelRequest): The request object containing model details.
            user_id (str): The ID of the user creating the model.
        Returns:
            CreateModelResponse: The response object containing the ID of the created model.
        """
        model_id = self.model_service.create_model(
            user_id=user_id,
            model_name=request.name,
            model_type=request.type,
            dimensions=request.dimensions,
            provider=request.provider,
            config=request.config,
        )
        return CreateModelResponse(id=model_id)

    def update_model(
        self, request: UpdateModelRequest, user_id: str
    ) -> UpdateModelResponse:
        """
        Handle database index update request

        Args:
            request (UpdateModelRequest): The request object containing updated model details.
            user_id (str): The ID of the user updating the model.
        Returns:
            UpdateModelResponse: A response object indicating the update was successful.
        """
        self.model_service.update_model(
            user_id=user_id,
            model_id=request.id,
            model_name=request.name,
            model_type=request.type,
            dimensions=request.dimensions,
            provider=request.provider,
            config=request.config,
        )
        return UpdateModelResponse(message="Model updated successfully")

    def list_models(self, user_id: str) -> List[ListModelsResponse]:
        """
        Handle list model request

        Args:
            user_id (str): The ID of the user whose models to list.
        Returns:
            List[ListModelsResponse]: A list of models available for the user.
        """
        indexes = self.model_service.list_models(user_id)
        return [ListModelsResponse(**index) for index in indexes]

    def delete_model(self, db_id: str, user_id: str) -> Dict[str, str]:
        """
        Handle database index deletion request

        Args:
            db_id (str): The ID of the database index to delete.
            user_id (str): The ID of the user requesting the deletion.
        Returns:
            Dict[str, str]: A message indicating the deletion was successful.
        """
        self.model_service.delete_model(db_id, user_id)
        return {"message": "Model deleted successfully"}
