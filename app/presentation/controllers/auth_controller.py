from typing import Any, Dict, List

from app.application.services.auth_service import AuthService
from app.presentation.schemas.auth_schemas import (
    AuthResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    GenApiKeyRequest,
    GenApiKeyResponse,
    LoginRequest,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RegisterRequest,
    RegisterResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    RevokeApiKeyRequest,
    UpdateUserRequest,
    UpdateUserResponse,
    ResendConfirmationEmailRequest,
    ResendConfirmationEmailResponse,
)


class AuthController:
    """Controller for authentication operations"""

    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    def resend_confirmation_email(
        self, request: ResendConfirmationEmailRequest
    ) -> ResendConfirmationEmailResponse:
        """
        Handle resend confirmation email request

        Args:
            request (ResendConfirmationEmailRequest): The request containing user email
        Returns:
            ResendConfirmationEmailResponse: The response confirming email was resent
        """
        message = self.auth_service.resend_confirmation_email(email=request.email)
        return ResendConfirmationEmailResponse(message=message)

    def generate_api_key(self, request: GenApiKeyRequest) -> GenApiKeyResponse:
        """
        Handle API key generation request

        Args:
            request (GenApiKeyRequest): The request containing user and project details
        Returns:
            GenApiKeyResponse: The response containing the generated API key and its ID
        """
        api_key, key_id = self.auth_service.generate_api_key(
            user_id=request.user_id,
            expires_in_days=request.expires_in_days,
            name=request.name,
        )
        return GenApiKeyResponse(api_key=api_key, key_id=key_id or "")

    def revoke_api_key(self, request: RevokeApiKeyRequest) -> Dict[str, str]:
        """
        Handle API key revocation request

        Args:
            request (RevokeApiKeyRequest): The request containing the API key ID to revoke
        Returns:
            Dict[str, str]: A message indicating the result of the revocation
        """
        self.auth_service.revoke_api_key(request.key_id)
        return {"message": "API key revoked successfully"}

    def list_api_keys(self, user_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Handle API key listing request

        Args:
            request (ListApiKeyRequest): The request containing project ID
            user_id (str): The ID of the user whose API keys are to be listed
        Returns:
            Dict[str, List[Dict[str, Any]]]: A dictionary containing a list of API keys
        """
        api_keys = self.auth_service.list_api_keys(user_id=user_id)
        return {"api_keys": api_keys}

    def login(self, request: LoginRequest) -> AuthResponse:
        """
        Handle user login request

        Args:
            request (LoginRequest): The login request containing email and password
        Returns:
            AuthResponse: The response containing authentication tokens
        """
        user_id, access_token, refresh_token, expires_in, name = self.auth_service.login(
            email=request.email, password=request.password
        )

        return AuthResponse(
            user_id=user_id,
            email=request.email,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
            name=name,
        )

    def register(self, request: RegisterRequest) -> RegisterResponse:
        """
        Handle user registration request

        Args:
            request (RegisterRequest): The registration request containing email, password, name, phone, and optional reference_code and company
        Returns:
            RegisterResponse: The response containing user info and message (no tokens when email validation required)
        """
        user_id, message = self.auth_service.register(
            email=request.email,
            password=request.password,
            name=request.name,
            phone=request.phone,
            reference_code=request.reference_code,
            company=request.company,
        )

        return RegisterResponse(
            user_id=user_id,
            email=request.email,
            message=message,
        )

    def refresh_token(self, request: RefreshTokenRequest) -> RefreshTokenResponse:
        """
        Handle token refresh request

        Args:
            request (RefreshTokenRequest): The refresh request containing refresh token
        Returns:
            RefreshTokenResponse: The response containing new access and refresh tokens
        """
        access_token, refresh_token, expires_in = self.auth_service.refresh_token(
            request.refresh_token
        )

        return RefreshTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
        )

    def update_user_profile(
        self, user_id: str, request: UpdateUserRequest
    ) -> UpdateUserResponse:
        """
        Handle user profile update request

        Args:
            user_id (str): The user ID from authentication
            request (UpdateUserRequest): The update request containing optional profile fields
        Returns:
            UpdateUserResponse: The response containing updated user profile
        """
        user_id, email, name, phone, company, reference_code = (
            self.auth_service.update_user_profile(
                user_id=user_id,
                name=request.name,
                phone=request.phone,
                company=request.company,
                reference_code=request.reference_code,
            )
        )

        return UpdateUserResponse(
            user_id=user_id,
            email=email,
            name=name,
            phone=phone,
            company=company,
            reference_code=reference_code,
        )

    def forgot_password(self, request: ForgotPasswordRequest) -> ForgotPasswordResponse:
        """
        Handle forgot password request

        Args:
            request (ForgotPasswordRequest): The forgot password request containing email
        Returns:
            ForgotPasswordResponse: The response confirming email was sent
        """
        message = self.auth_service.forgot_password(email=request.email)
        return ForgotPasswordResponse(message=message)

    def reset_password(self, request: ResetPasswordRequest) -> ResetPasswordResponse:
        """
        Handle password reset request

        Args:
            request (ResetPasswordRequest): The reset request containing access token and new password
        Returns:
            ResetPasswordResponse: The response confirming password was reset
        """
        message = self.auth_service.reset_password(
            access_token=request.access_token, new_password=request.new_password
        )
        return ResetPasswordResponse(message=message)
