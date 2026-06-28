from unittest.mock import Mock
from app.presentation.controllers.prompt_controller import PromptController
from app.application.services.prompt_service import PromptService
from app.presentation.schemas.prompt_schemas import (
    CreatePromptRequest,
    CreatePromptResponse,
    ListPromptsResponse,
)


class TestPromptController:
    def setup_method(self):
        self.mock_service = Mock(spec=PromptService)
        self.controller = PromptController(self.mock_service)

    def test_create_prompt_success(self):
        request = CreatePromptRequest(name="prompt", prompt="Test prompt")
        self.mock_service.create_prompt.return_value = "prompt-abc"

        response = self.controller.create_prompt(request, user_id="user-123")

        assert isinstance(response, CreatePromptResponse)
        assert response.id == "prompt-abc"
        self.mock_service.create_prompt.assert_called_once_with(
            user_id="user-123",
            prompt_name="prompt",
            prompt_text="Test prompt",
        )

    def test_list_prompts_success(self):
        prompts = [
            {
                "id": "m1",
                "name": "prompt1",
                "prompt": "Sample prompt 1",
            },
            {
                "id": "m2",
                "name": "prompt2",
                "prompt": "Sample prompt 2",
            },
        ]
        self.mock_service.list_prompts.return_value = prompts

        result = self.controller.list_prompts("user-123")

        assert isinstance(result, list)
        assert all(isinstance(m, ListPromptsResponse) for m in result)
        assert result[0].id == "m1"
        assert result[1].prompt == "Sample prompt 2"

        self.mock_service.list_prompts.assert_called_once_with("user-123")

    def test_delete_prompt_success(self):
        response = self.controller.delete_prompt("prompt-id", "user-123")
        assert response == {"message": "Prompt deleted successfully"}
        self.mock_service.delete_prompt.assert_called_once_with("prompt-id", "user-123")
