from unittest.mock import Mock
from app.presentation.controllers.auth_controller import AuthController
from app.application.services.auth_service import AuthService
from app.presentation.schemas.auth_schemas import (
    GenApiKeyRequest,
    RevokeApiKeyRequest,
)


class TestAuthController:
    """Unit tests for AuthController"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_auth_service = Mock(spec=AuthService)
        self.auth_controller = AuthController(self.mock_auth_service)

    def test_generate_api_key_success(self):
        """Test successful API key generation"""
        request = GenApiKeyRequest(
            user_id="test-user", expires_in_days=30, name="Test Key"
        )

        self.mock_auth_service.generate_api_key.return_value = (
            "test-api-key",
            "test-key-id",
        )

        result = self.auth_controller.generate_api_key(request)

        assert result.api_key == "test-api-key"
        assert result.key_id == "test-key-id"
        self.mock_auth_service.generate_api_key.assert_called_once_with(
            user_id="test-user", expires_in_days=30, name="Test Key"
        )

    def test_generate_api_key_with_none_key_id(self):
        """Test API key generation when key_id is None"""
        request = GenApiKeyRequest(
            user_id="test-user", expires_in_days=30, name="Test Key"
        )

        self.mock_auth_service.generate_api_key.return_value = ("test-api-key", None)

        result = self.auth_controller.generate_api_key(request)

        assert result.api_key == "test-api-key"
        assert result.key_id == ""

    def test_revoke_api_key_success(self):
        """Test successful API key revocation"""
        request = RevokeApiKeyRequest(key_id="test-key-id")

        result = self.auth_controller.revoke_api_key(request)

        assert result == {"message": "API key revoked successfully"}
        self.mock_auth_service.revoke_api_key.assert_called_once_with("test-key-id")

    def test_list_api_keys_success(self):
        """Test successful API key listing"""
        expected_keys = [
            {"key_id": "key1", "expires_at": "2024-01-01"},
            {"key_id": "key2", "expires_at": "2024-01-02"},
        ]

        self.mock_auth_service.list_api_keys.return_value = expected_keys

        result = self.auth_controller.list_api_keys(user_id="test-user")

        assert result == {"api_keys": expected_keys}
        self.mock_auth_service.list_api_keys.assert_called_once_with(
            user_id="test-user"
        )
