from unittest.mock import Mock, patch

import pytest

from app.application.exceptions import (
    ModelCreationException,
    ModelDeletionException,
    ModelListingException,
    ModelNotFoundException,
    ModelRetrievalException,
)
from app.application.services.model_service import ModelService


class TestModelService:
    def setup_method(self):
        self.model_service = ModelService()

    @patch("app.application.services.model_service.fetch_items")
    def test_get_builtin_models_success(self, mock_supabase):
        mock_supabase.return_value = [{"name": "builtin"}]
        result = self.model_service.get_builtin_models()
        assert result == [{"name": "builtin"}]

    @patch("app.application.services.model_service.fetch_items")
    def test_get_builtin_models_failure(self, mock_supabase):
        mock_supabase.side_effect = Exception("db error")
        with pytest.raises(
            ModelRetrievalException, match="Failed to get builtin models: db error"
        ):
            self.model_service.get_builtin_models()

    @patch("app.application.services.model_service.fetch_items")
    def test_get_user_defined_models_success(self, mock_supabase):
        mock_supabase.return_value = [{"name": "custom"}]

        result = self.model_service.get_user_defined_models("user123")
        assert result == [{"name": "custom"}]

    @patch("app.application.services.model_service.fetch_items")
    def test_get_user_defined_models_failure(self, mock_supabase):
        mock_supabase.side_effect = Exception("fail")
        with pytest.raises(
            ModelRetrievalException, match="Failed to get user-defined models: fail"
        ):
            self.model_service.get_user_defined_models("user123")

    @patch.object(ModelService, "get_builtin_models")
    @patch.object(ModelService, "get_user_defined_models")
    def test_list_models_success(self, mock_user_models, mock_builtin_models):
        mock_builtin_models.return_value = [{"name": "builtin"}]
        mock_user_models.return_value = [{"name": "custom"}]
        result = self.model_service.list_models(
            "user123",
        )
        assert result == [{"name": "builtin"}, {"name": "custom"}]

    @patch.object(
        ModelService, "get_user_defined_models", side_effect=Exception("list error")
    )
    def test_list_models_failure(self, _):
        with pytest.raises(
            ModelListingException, match="Failed to list models: list error"
        ):
            self.model_service.list_models(
                "user123",
            )

    @patch("app.application.services.model_service.add_item")
    def test_create_model_success(self, mock_supabase):
        mock_supabase.return_value = Mock(data=[{"id": "abc123"}])
        model_id = self.model_service.create_model(
            user_id="u1",
            model_name="gpt-4",
            model_type="chat",
            dimensions=768,
            provider="openai",
            config={"version": "1"},
        )
        assert model_id == "abc123"

    @patch("app.application.services.model_service.add_item")
    def test_create_model_failure(self, mock_supabase):
        mock_supabase.side_effect = Exception("insert fail")
        with pytest.raises(
            ModelCreationException, match="Failed to generate model: insert fail"
        ):
            self.model_service.create_model(
                "u1",
                "gpt-4",
                "chat",
                768,
                "azure_openai",
                {"version": "1"},
            )

    @patch("app.application.services.model_service.delete_item")
    def test_delete_model_success(self, mock_supabase):
        mock_supabase.return_value = Mock(data=[{"id": "model1"}])
        self.model_service.delete_model(
            "model1",
            "user1",
        )

    @patch("app.application.services.model_service.delete_item")
    def test_delete_model_not_found(self, mock_supabase):
        mock_supabase.return_value = Mock(data=[])
        with pytest.raises(ModelNotFoundException, match="model model1 not found."):
            self.model_service.delete_model(
                "model1",
                "user1",
            )

    @patch("app.application.services.model_service.delete_item")
    def test_delete_model_failure(self, mock_supabase):
        mock_supabase.side_effect = Exception("delete fail")
        with pytest.raises(
            ModelDeletionException, match="Failed to delete model: delete fail"
        ):
            self.model_service.delete_model(
                "model1",
                "user1",
            )

    @patch("app.application.services.model_service.fetch_items")
    @patch("app.application.services.model_service.decrypt_dict")
    def test_get_model_success(self, mock_decrypt_model, mock_supabase):
        mock_supabase.return_value = [
            {"id": "model1", "name": "my-model", "config": "adasdasd554da545"}
        ]
        mock_decrypt_model.return_value = {"key": "value"}

        result = self.model_service.get_model(
            "model1",
        )
        assert result["id"] == "model1"

    @patch("app.application.services.model_service.fetch_items")
    def test_get_model_failure(self, mock_supabase):
        mock_supabase.side_effect = Exception("query error")
        with pytest.raises(
            ModelNotFoundException, match="Failed to get model: query error"
        ):
            self.model_service.get_model(
                "model1",
            )
