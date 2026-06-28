import pytest
from unittest.mock import MagicMock
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
        self.mock_provider = MagicMock()
        self.auth_service = AuthService(self.mock_provider)

    def test_generate_api_key_success(self):
        """Test successful API key generation"""
        user_id = "test-user"
        expires_in_days = 30
        name = "Test Key"

        self.mock_provider.generate_api_key.return_value = ("test-api-key", "test-key-id")

        api_key, key_id = self.auth_service.generate_api_key(user_id, expires_in_days, name)

        assert api_key == "test-api-key"
        assert key_id == "test-key-id"
        self.mock_provider.generate_api_key.assert_called_once_with(user_id, expires_in_days, name)

    def test_generate_api_key_failure(self):
        """Test API key generation failure"""
        user_id = "test-user"
        expires_in_days = 30
        name = "Test Key"

        self.mock_provider.generate_api_key.side_effect = ApiKeyGenerationException("Failed to generate API key: Database error")

        with pytest.raises(
            ApiKeyGenerationException,
            match="Failed to generate API key: Database error",
        ):
            self.auth_service.generate_api_key(user_id, expires_in_days, name)

    def test_revoke_api_key_success(self):
        """Test successful API key revocation"""
        key_id = "test-key-id"

        self.auth_service.revoke_api_key(key_id)

        self.mock_provider.revoke_api_key.assert_called_once_with(key_id)

    def test_revoke_api_key_failure(self):
        """Test API key revocation failure"""
        key_id = "test-key-id"

        self.mock_provider.revoke_api_key.side_effect = ApiKeyRevokeException("Failed to revoke API key: Key not found")

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

        self.mock_provider.list_api_keys.return_value = expected_keys

        result = self.auth_service.list_api_keys(user_id)

        assert result == expected_keys
        self.mock_provider.list_api_keys.assert_called_once_with(user_id)

    def test_list_api_keys_failure(self):
        """Test API key listing failure"""
        user_id = "test-user"

        self.mock_provider.list_api_keys.side_effect = ApiKeyListException("Failed to list API keys: Database connection failed")

        with pytest.raises(
            ApiKeyListException,
            match="Failed to list API keys: Database connection failed",
        ):
            self.auth_service.list_api_keys(user_id)