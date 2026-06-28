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
    ResendConfirmationEmailRequest,
    ResendConfirmationEmailResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    RevokeApiKeyRequest,
    UpdateUserRequest,
    UpdateUserResponse,
)


class AuthController:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    def resend_confirmation_email(
        self, request: ResendConfirmationEmailRequest
    ) -> ResendConfirmationEmailResponse:
        message = self.auth_service.resend_confirmation_email(email=request.email)
        return ResendConfirmationEmailResponse(message=message)

    def generate_api_key(self, request: GenApiKeyRequest) -> GenApiKeyResponse:
        api_key, key_id = self.auth_service.generate_api_key(
            user_id=request.user_id,
            expires_in_days=request.expires_in_days,
            name=request.name,
        )
        return GenApiKeyResponse(api_key=api_key, key_id=key_id or "")

    def revoke_api_key(self, request: RevokeApiKeyRequest) -> Dict[str, str]:
        self.auth_service.revoke_api_key(request.key_id)
        return {"message": "API key revoked successfully"}

    def list_api_keys(self, user_id: str) -> Dict[str, List[Dict[str, Any]]]:
        api_keys = self.auth_service.list_api_keys(user_id=user_id)
        return {"api_keys": api_keys}

    def login(self, request: LoginRequest) -> AuthResponse:
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
        user_id, message = self.auth_service.register(
            email=request.email,
            password=request.password,
            name=request.name,
            phone=request.phone,
            company=request.company,
        )
        return RegisterResponse(
            user_id=user_id,
            email=request.email,
            message=message,
        )

    def refresh_token(self, request: RefreshTokenRequest) -> RefreshTokenResponse:
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
        user_id, email, name, phone, company = (
            self.auth_service.update_user_profile(
                user_id=user_id,
                name=request.name,
                phone=request.phone,
                company=request.company,
            )
        )
        return UpdateUserResponse(
            user_id=user_id,
            email=email,
            name=name,
            phone=phone,
            company=company,
        )

    def forgot_password(self, request: ForgotPasswordRequest) -> ForgotPasswordResponse:
        message = self.auth_service.forgot_password(email=request.email)
        return ForgotPasswordResponse(message=message)

    def reset_password(self, request: ResetPasswordRequest) -> ResetPasswordResponse:
        message = self.auth_service.reset_password(
            access_token=request.access_token, new_password=request.new_password
        )
        return ResetPasswordResponse(message=message)