from typing import Dict, List

from app.application.services.prompt_service import PromptService
from app.presentation.schemas.prompt_schemas import (
    CreatePromptRequest,
    CreatePromptResponse,
    ListPromptsResponse,
    UpdatePromptRequest,
    UpdatePromptResponse,
)


class PromptController:
    """Controller for database index operations"""

    def __init__(self, prompt_service: PromptService):
        self.prompt_service = prompt_service

    def create_prompt(
        self, request: CreatePromptRequest, user_id: str
    ) -> CreatePromptResponse:
        """
        Handle prompt creation request

        Args:
            request (CreatePromptRequest): The request object containing prompt details.
            user_id (str): The ID of the user creating the prompt.
        Returns:
            CreatePromptResponse: The response object containing the ID of the created prompt.
        """
        prompt_id = self.prompt_service.create_prompt(
            user_id=user_id,
            prompt_name=request.name,
            prompt_text=request.prompt,
        )
        return CreatePromptResponse(id=prompt_id)

    def list_prompts(self, user_id: str) -> List[ListPromptsResponse]:
        """
        Handle list prompt request

        Args:
            user_id (str): The ID of the user whose prompts to list.
        Returns:
            List[ListPromptsResponse]: A list of prompts available for the user.
        """
        indexes = self.prompt_service.list_prompts(user_id)
        return [ListPromptsResponse(**index) for index in indexes]

    def delete_prompt(self, prompt_id: str, user_id: str) -> Dict[str, str]:
        """
        Handle prompt deletion request

        Args:
            prompt_id (str): The ID of the database index to delete.
            user_id (str): The ID of the user requesting the deletion.
        Returns:
            Dict[str, str]: A message indicating the deletion was successful.
        """
        self.prompt_service.delete_prompt(prompt_id, user_id)
        return {"message": "Prompt deleted successfully"}

    def update_prompt(
        self, request: UpdatePromptRequest, user_id: str
    ) -> UpdatePromptResponse:
        """
        Handle prompt update request

        Args:
            request (UpdatePromptRequest): The request object containing updated prompt details.
            user_id (str): The ID of the user updating the prompt.
        Returns:
            UpdatePromptResponse: A message indicating the update was successful.
        """
        self.prompt_service.update_prompt(
            user_id=user_id,
            prompt_id=request.id,
            prompt_name=request.name,
            prompt_text=request.prompt,
        )
        return UpdatePromptResponse(message="Prompt updated successfully")
