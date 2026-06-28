import pytest
from unittest.mock import patch
from app.application.exceptions import (
    ApiKeyGenerationException,
    ApiKeyListException,
    ApiKeyRevokeException,
)
from app.application.services.auth_service import AuthService


class TestAuthService:
    """Unit tests for AuthService"""

    def setup_method(self):
        """Set up test fixtures"""
        self.auth_service = AuthService()

    def test_generate_api_key_success(self):
        """Test successful API key generation"""
        user_id = "test-user"
        expires_in_days = 30
        name = "Test Key"

        with patch(
            "app.application.services.auth_service.create_api_key"
        ) as mock_create:
            mock_create.return_value = ("test-api-key", "test-key-id")

            api_key, key_id = self.auth_service.generate_api_key(
                user_id, expires_in_days, name
            )

            assert api_key == "test-api-key"
            assert key_id == "test-key-id"
            mock_create.assert_called_once_with(user_id, expires_in_days, name)

    def test_generate_api_key_failure(self):
        """Test API key generation failure"""
        user_id = "test-user"
        expires_in_days = 30
        name = "Test Key"

        with patch(
            "app.application.services.auth_service.create_api_key"
        ) as mock_create:
            mock_create.side_effect = Exception("Database error")

            with pytest.raises(
                ApiKeyGenerationException,
                match="Failed to generate API key: Database error",
            ):
                self.auth_service.generate_api_key(user_id, expires_in_days, name)

    def test_revoke_api_key_success(self):
        """Test successful API key revocation"""
        key_id = "test-key-id"

        with patch(
            "app.application.services.auth_service.revoke_api_key"
        ) as mock_revoke:
            self.auth_service.revoke_api_key(key_id)

            mock_revoke.assert_called_once_with(key_id)

    def test_revoke_api_key_failure(self):
        """Test API key revocation failure"""
        key_id = "test-key-id"

        with patch(
            "app.application.services.auth_service.revoke_api_key"
        ) as mock_revoke:
            mock_revoke.side_effect = Exception("Key not found")

            with pytest.raises(
                ApiKeyRevokeException, match="Failed to revoke API key: Key not found"
            ):
                self.auth_service.revoke_api_key(key_id)

    def test_list_api_keys_success(self):
        """Test successful API key listing"""
        user_id = "test-user"
        expected_keys = [
            {"key_id": "key1", "expires_at": "2024-01-01"},
            {"key_id": "key2", "expires_at": "2024-01-02"},
        ]

        with patch("app.application.services.auth_service.list_api_keys") as mock_list:
            mock_list.return_value = expected_keys

            result = self.auth_service.list_api_keys(user_id)

            assert result == expected_keys
            mock_list.assert_called_once_with(user_id)

    def test_list_api_keys_failure(self):
        """Test API key listing failure"""
        user_id = "test-user"

        with patch("app.application.services.auth_service.list_api_keys") as mock_list:
            mock_list.side_effect = Exception("Database connection failed")

            with pytest.raises(
                ApiKeyListException,
                match="Failed to list API keys: Database connection failed",
            ):
                self.auth_service.list_api_keys(user_id)
