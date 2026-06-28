import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.infra.auth import get_user
from app.main import create_application


@pytest.fixture
def client():
    app = create_application()

    # Override `get_user` to return a fake user ID for protected endpoints
    app.dependency_overrides[get_user] = lambda: "test-user-id"

    return TestClient(app)


def test_generate_api_key_success(client, mocker):
    mock_generate = mocker.patch(
        "app.presentation.controllers.auth_controller.AuthController.generate_api_key"
    )
    mock_generate.return_value = mocker.Mock(api_key="test-api-key", key_id="key-123")

    payload = {
        "user_id": "user-1",
        "expires_in_days": 30,
        "name": "My API Key",
    }

    response = client.post("/auth/generate-api-key", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "api_key": "test-api-key",
        "key_id": "key-123",
    }


def test_revoke_api_key_success(client, mocker):
    mock_revoke = mocker.patch(
        "app.presentation.controllers.auth_controller.AuthController.revoke_api_key"
    )
    mock_revoke.return_value = {"message": "API key revoked successfully"}

    payload = {"key_id": "key-123"}

    response = client.post("/auth/revoke-api-key", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"message": "API key revoked successfully"}


def test_list_api_keys_success(client, mocker):
    mock_list = mocker.patch(
        "app.presentation.controllers.auth_controller.AuthController.list_api_keys"
    )
    mock_list.return_value = [
        {"key_id": "key1", "created_at": "2025-01-01"},
        {"key_id": "key2", "created_at": "2025-01-02"},
    ]

    response = client.get("/auth/list-api-keys/test_user")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {"key_id": "key1", "created_at": "2025-01-01"},
        {"key_id": "key2", "created_at": "2025-01-02"},
    ]


def test_revoke_api_key_unauthorized(mocker):
    """
    Tests the revoke endpoint when user is not authenticated (no API key).
    """
    app = create_application()

    # Simulate unauthorized by returning None
    app.dependency_overrides[get_user] = lambda: None

    test_client = TestClient(app)

    payload = {"key_id": "key-123"}
    response = test_client.post("/auth/revoke-api-key", json=payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "User not authenticated"


# JWT Authentication Tests
def test_auth_info_with_api_key(client, mocker):
    """Test auth info endpoint when API key authentication is used"""
    mocker.patch(
        "app.application.services.auth_service.AuthService.get_user_details",
        return_value=("user@example.com", None),
    )
    response = client.get("/auth/auth-info", headers={"X-API-Key": "test-api-key"})

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["method"] == "api_key"
    assert data["user_id"] == "test-user-id"
    assert data["email"] == "user@example.com"


# Login and Register Tests
def test_login_success(client, mocker):
    """Test login endpoint with valid credentials"""
    mock_login = mocker.patch("app.application.services.auth_service.AuthService.login")
    mock_login.return_value = ("user-123", "access-token", "refresh-token", 3600, "Test User")

    payload = {"email": "test@example.com", "password": "password123"}

    response = client.post("/auth/login", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user-123"
    assert data["email"] == "test@example.com"
    assert data["access_token"] == "access-token"
    assert data["refresh_token"] == "refresh-token"
    assert data["expires_in"] == 3600
    assert data["token_type"] == "bearer"


def test_login_failure(client, mocker):
    """Test login endpoint with invalid credentials"""
    from app.application.exceptions import InvalidCredentialsException

    mock_login = mocker.patch("app.application.services.auth_service.AuthService.login")
    mock_login.side_effect = InvalidCredentialsException("Invalid email or password")

    payload = {"email": "test@example.com", "password": "wrongpassword"}

    response = client.post("/auth/login", json=payload)

    assert response.status_code == 500  # Error response


def test_register_success(client, mocker):
    """Test register endpoint with valid data"""
    mock_register = mocker.patch(
        "app.application.services.auth_service.AuthService.register"
    )
    mock_register.return_value = (
        "user-456",
        "Registration successful. Please check your email to verify your account.",
    )

    payload = {
        "email": "newuser@example.com",
        "password": "password123",
        "name": "New User",
        "phone": "+1234567890",
        "reference_code": "REF123",
        "company": "Acme Corp",
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == "user-456"
    assert data["email"] == "newuser@example.com"
    assert (
        data["message"]
        == "Registration successful. Please check your email to verify your account."
    )


def test_register_failure(client, mocker):
    """Test register endpoint with invalid data"""
    from app.application.exceptions import EmailAlreadyInUseException

    mock_register = mocker.patch(
        "app.application.services.auth_service.AuthService.register"
    )
    mock_register.side_effect = EmailAlreadyInUseException("Email already exists")

    payload = {
        "email": "existing@example.com",
        "password": "password123",
        "name": "Test User",
        "phone": "+1234567890",
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 500  # Error response


def test_register_duplicate_email(client, mocker):
    """Test register endpoint with duplicate email"""
    from app.application.exceptions import EmailAlreadyInUseException

    mock_register = mocker.patch(
        "app.application.services.auth_service.AuthService.register"
    )
    mock_register.side_effect = EmailAlreadyInUseException(
        "Email address is already in use"
    )

    payload = {
        "email": "duplicate@example.com",
        "password": "password123",
        "name": "Test User",
        "phone": "+1234567890",
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 500
    data = response.json()
    assert "Email address is already in use" in data["detail"]


# Phone uniqueness test removed - no longer checking phone uniqueness


def test_refresh_token_success(client, mocker):
    """Test refresh token endpoint with valid refresh token"""
    mock_refresh = mocker.patch(
        "app.application.services.auth_service.AuthService.refresh_token"
    )
    mock_refresh.return_value = ("new-access-token", "new-refresh-token", 3600)

    payload = {"refresh_token": "valid-refresh-token"}

    response = client.post("/auth/refresh", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "new-access-token"
    assert data["refresh_token"] == "new-refresh-token"
    assert data["expires_in"] == 3600
    assert data["token_type"] == "bearer"


def test_refresh_token_failure(client, mocker):
    """Test refresh token endpoint with invalid refresh token"""
    mock_refresh = mocker.patch(
        "app.application.services.auth_service.AuthService.refresh_token"
    )
    mock_refresh.side_effect = Exception("Invalid refresh token")

    payload = {"refresh_token": "invalid-refresh-token"}

    response = client.post("/auth/refresh", json=payload)

    assert response.status_code == 500  # Error response


import pytest
from fastapi.testclient import TestClient

from app.infra.auth import get_user
from app.main import create_application


@pytest.fixture
def client():
    app = create_application()
    app.dependency_overrides[get_user] = lambda: "test-user-id"
    return TestClient(app)


def test_update_user_profile_success(client, mocker):
    """Test update user profile endpoint with valid data"""
    mock_update = mocker.patch(
        "app.application.services.auth_service.AuthService.update_user_profile"
    )
    mock_update.return_value = (
        "test-user-id",
        "test@example.com",
        "Updated Name",
        "+1234567890",
        "Updated Company",
    )

    payload = {
        "name": "Updated Name",
        "phone": "+1234567890",
        "company": "Updated Company",
    }

    response = client.put("/auth/update-profile", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "test-user-id"
    assert data["email"] == "test@example.com"
    assert data["name"] == "Updated Name"
    assert data["phone"] == "+1234567890"
    assert data["company"] == "Updated Company"
    assert "successfully" in data["message"]


def test_update_user_profile_partial_update(client, mocker):
    """Test update user profile with partial data"""
    mock_update = mocker.patch(
        "app.application.services.auth_service.AuthService.update_user_profile"
    )
    mock_update.return_value = (
        "test-user-id",
        "test@example.com",
        "Updated Name",
        "+1234567890",
        None,
    )

    payload = {"name": "Updated Name"}

    response = client.put("/auth/update-profile", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["company"] is None


def test_update_user_profile_unauthorized(client):
    """Test update user profile without authentication"""
    app = create_application()
    app.dependency_overrides[get_user] = lambda: None
    test_client = TestClient(app)

    payload = {"name": "Updated Name"}

    response = test_client.put("/auth/update-profile", json=payload)

    assert response.status_code == 401
    assert "Authentication required" in response.json()["detail"]


def test_forgot_password_success(client, mocker):
    """Test forgot password endpoint with valid email"""
    mock_forgot = mocker.patch(
        "app.application.services.auth_service.AuthService.forgot_password"
    )
    mock_forgot.return_value = "Password reset email sent. Please check your inbox."

    payload = {"email": "test@example.com"}

    response = client.post("/auth/forgot-password", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "Password reset email sent" in data["message"]


def test_forgot_password_invalid_email(client, mocker):
    """Test forgot password with invalid email format"""
    from app.application.exceptions import InvalidEmailFormatException

    mock_forgot = mocker.patch(
        "app.application.services.auth_service.AuthService.forgot_password"
    )
    mock_forgot.side_effect = InvalidEmailFormatException("Invalid email format")

    payload = {"email": "invalid-email"}

    response = client.post("/auth/forgot-password", json=payload)

    assert response.status_code == 500
    data = response.json()
    assert "Invalid email format" in data["detail"]


def test_reset_password_success(client, mocker):
    """Test reset password endpoint with valid token and password"""
    mock_reset = mocker.patch(
        "app.application.services.auth_service.AuthService.reset_password"
    )
    mock_reset.return_value = (
        "Password reset successfully. You can now log in with your new password."
    )

    payload = {
        "access_token": "valid-reset-token",
        "new_password": "newpassword123",
    }

    response = client.post("/auth/reset-password", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "Password reset successfully" in data["message"]


def test_reset_password_invalid_token(client, mocker):
    """Test reset password with invalid token"""
    from app.application.exceptions import InvalidTokenException

    mock_reset = mocker.patch(
        "app.application.services.auth_service.AuthService.reset_password"
    )
    mock_reset.side_effect = InvalidTokenException("Invalid or expired token")

    payload = {
        "access_token": "invalid-token",
        "new_password": "newpassword123",
    }

    response = client.post("/auth/reset-password", json=payload)

    assert response.status_code == 500
    data = response.json()
    assert "Invalid or expired token" in data["detail"]


def test_reset_password_weak_password(client, mocker):
    """Test reset password with weak password"""
    from app.application.exceptions import PasswordTooWeakException

    mock_reset = mocker.patch(
        "app.application.services.auth_service.AuthService.reset_password"
    )
    mock_reset.side_effect = PasswordTooWeakException("Password is too weak")

    payload = {
        "access_token": "valid-reset-token",
        "new_password": "123",
    }

    response = client.post("/auth/reset-password", json=payload)

    assert response.status_code == 500
    data = response.json()
    assert "Password is too weak" in data["detail"]
