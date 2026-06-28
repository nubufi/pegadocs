from unittest.mock import Mock
from app.presentation.controllers.model_controller import ModelController
from app.application.services.model_service import ModelService
from app.presentation.schemas.model_schemas import (
    CreateModelRequest,
    CreateModelResponse,
    ListModelsResponse,
)


class TestModelController:
    def setup_method(self):
        self.mock_service = Mock(spec=ModelService)
        self.controller = ModelController(self.mock_service)

    def test_create_model_success(self):
        request = CreateModelRequest(
            name="embedding-model",
            type="embedding",
            dimensions=1536,
            provider="azure_openai",
            config={"version": "1"},
        )
        self.mock_service.create_model.return_value = "model-abc"

        response = self.controller.create_model(request, user_id="user-123")

        assert isinstance(response, CreateModelResponse)
        assert response.id == "model-abc"
        self.mock_service.create_model.assert_called_once_with(
            user_id="user-123",
            model_name="embedding-model",
            model_type="embedding",
            dimensions=1536,
            provider="azure_openai",
            config={"version": "1"},
        )

    def test_list_models_success(self):
        models = [
            {
                "id": "m1",
                "name": "model1",
                "type": "chat",
                "dimensions": 512,
                "provider": "azure_openai",
                "config": {"version": "1"},
            },
            {
                "id": "m2",
                "name": "model2",
                "type": "embedding",
                "dimensions": 1024,
                "provider": "azure_openai",
                "config": {"version": "2"},
            },
        ]
        self.mock_service.list_models.return_value = models

        result = self.controller.list_models("user-123")

        assert isinstance(result, list)
        assert all(isinstance(m, ListModelsResponse) for m in result)
        assert result[0].id == "m1"
        assert result[1].provider == "azure_openai"

        self.mock_service.list_models.assert_called_once_with("user-123")

    def test_delete_model_success(self):
        response = self.controller.delete_model("model-id", "user-123")
        assert response == {"message": "Model deleted successfully"}
        self.mock_service.delete_model.assert_called_once_with("model-id", "user-123")
