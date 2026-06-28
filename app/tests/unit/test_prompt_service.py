from unittest.mock import Mock, patch

import pytest

from app.application.exceptions import (
    PromptCreationException,
    PromptDeletionException,
    PromptListingException,
    PromptNotFoundException,
    PromptRetrievalException,
)
from app.application.services.prompt_service import PromptService


class TestPromptService:
    def setup_method(self):
        self.prompt_service = PromptService()

    @patch("app.application.services.prompt_service.fetch_items")
    def test_get_builtin_prompt_success(self, mock_supabase):
        mock_supabase.return_value = [{"name": "builtin"}]
        result = self.prompt_service.get_builtin_prompts()
        assert result == [{"name": "builtin"}]

    @patch("app.application.services.prompt_service.fetch_items")
    def test_get_builtin_prompt_failure(self, mock_supabase):
        mock_supabase.side_effect = Exception("db error")
        with pytest.raises(
            PromptRetrievalException, match="Failed to get builtin prompts: db error"
        ):
            self.prompt_service.get_builtin_prompts()

    @patch("app.application.services.prompt_service.fetch_items")
    def test_get_user_defined_prompt_success(self, mock_supabase):
        mock_supabase.return_value = [{"name": "custom"}]
        result = self.prompt_service.get_user_defined_prompts("user123")
        assert result == [{"name": "custom"}]

    @patch("app.application.services.prompt_service.fetch_items")
    def test_get_user_defined_prompt_failure(self, mock_supabase):
        mock_supabase.side_effect = Exception("fail")
        with pytest.raises(
            PromptRetrievalException, match="Failed to get user-defined prompts: fail"
        ):
            self.prompt_service.get_user_defined_prompts("user123")

    @patch.object(PromptService, "get_builtin_prompts")
    @patch.object(PromptService, "get_user_defined_prompts")
    def test_list_prompt_success(self, mock_user_prompt, mock_builtin_prompt):
        mock_builtin_prompt.return_value = [{"name": "builtin"}]
        mock_user_prompt.return_value = [{"name": "custom"}]
        result = self.prompt_service.list_prompts(
            "user123",
        )
        assert result == [{"name": "builtin"}, {"name": "custom"}]

    @patch.object(
        PromptService, "get_user_defined_prompts", side_effect=Exception("list error")
    )
    def test_list_prompt_failure(self, _):
        with pytest.raises(
            PromptListingException, match="Failed to list prompts: list error"
        ):
            self.prompt_service.list_prompts(
                "user123",
            )

    @patch("app.application.services.prompt_service.add_item")
    def test_create_prompt_success(self, mock_supabase):
        mock_supabase.return_value = Mock(data=[{"id": "abc123"}])
        prompt_id = self.prompt_service.create_prompt(
            user_id="u1",
            prompt_name="test",
            prompt_text="test",
        )
        assert prompt_id == "abc123"

    @patch("app.application.services.prompt_service.add_item")
    def test_create_prompt_failure(self, mock_supabase):
        mock_supabase.side_effect = Exception("insert fail")
        with pytest.raises(
            PromptCreationException, match="Failed to generate prompt: insert fail"
        ):
            self.prompt_service.create_prompt(
                user_id="u1",
                prompt_name="test",
                prompt_text="test",
            )

    @patch("app.application.services.prompt_service.delete_item")
    def test_delete_prompt_success(self, mock_supabase):
        mock_supabase.return_value = Mock(data=[{"id": "prompt1"}])
        self.prompt_service.delete_prompt("prompt1", "user1")

    @patch("app.application.services.prompt_service.delete_item")
    def test_delete_prompt_not_found(self, mock_supabase):
        mock_supabase.return_value = Mock(data=[])
        with pytest.raises(PromptNotFoundException, match="prompt prompt1 not found."):
            self.prompt_service.delete_prompt("prompt1", "user1")

    @patch("app.application.services.prompt_service.delete_item")
    def test_delete_prompt_failure(self, mock_supabase):
        mock_supabase.side_effect = Exception("delete fail")
        with pytest.raises(
            PromptDeletionException, match="Failed to delete prompt: delete fail"
        ):
            self.prompt_service.delete_prompt("prompt1", "user1")

    @patch("app.application.services.prompt_service.fetch_items")
    def test_get_prompt_success(self, mock_supabase):
        mock_supabase.return_value = [
            {"id": "prompt1", "name": "my-prompt", "config": "adasdasd554da545"}
        ]
        result = self.prompt_service.get_prompt("prompt1")
        assert result["id"] == "prompt1"

    @patch("app.application.services.prompt_service.fetch_items")
    def test_get_prompt_failure(self, mock_supabase):
        mock_supabase.side_effect = Exception("query error")
        with pytest.raises(
            PromptNotFoundException, match="Failed to get prompt: query error"
        ):
            self.prompt_service.get_prompt("prompt1")
