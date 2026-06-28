from typing import Optional, List

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import JSONResponse

from app.application.services.auth_service import AuthService
from app.infra.auth import get_user
from app.infra.factories.auth_provider import AuthProviderFactory
from app.infra.utils.fastapi_utils import gen_error_response
from app.presentation.controllers.auth_controller import AuthController
from app.presentation.schemas.auth_schemas import (
    AccountLockedErrorResponse,
    AuthMethodResponse,
    AuthResponse,
    EmailAlreadyInUseErrorResponse,
    EmailNotVerifiedErrorResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    GenApiKeyRequest,
    GenApiKeyResponse,
    InvalidCredentialsErrorResponse,
    InvalidEmailFormatErrorResponse,
    InvalidTokenErrorResponse,
    ListApiKeyResponse,
    LoginRequest,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RegisterRequest,
    RegisterResponse,
    ResendConfirmationEmailResponse,
    ResendConfirmationEmailRequest,
    ResetPasswordRequest,
    ResetPasswordResponse,
    RevokeApiKeyRequest,
    TokenExpiredErrorResponse,
    UpdateUserRequest,
    UpdateUserResponse,
)

auth_router = APIRouter()

PROVIDER = AuthProviderFactory.get_provider()


def _get_auth_service() -> AuthService:
    return AuthService(PROVIDER)


def _get_auth_controller() -> AuthController:
    return AuthController(_get_auth_service())


@auth_router.post("/login", summary="Login user with email and password",
    response_model=AuthResponse,
    responses={
        400: {"model": InvalidEmailFormatErrorResponse, "description": "Invalid email format"},
        401: {"model": InvalidCredentialsErrorResponse, "description": "Invalid credentials"},
        403: {"model": EmailNotVerifiedErrorResponse, "description": "Email not verified"},
        423: {"model": AccountLockedErrorResponse, "description": "Account locked"},
        500: {"model": AuthResponse, "description": "Internal server error"},
    }, tags=["auth"])
def login(input: LoginRequest):
    controller = _get_auth_controller()
    try:
        result = controller.login(input)
        return JSONResponse(content={
            "user_id": result.user_id, "email": result.email,
            "access_token": result.access_token, "refresh_token": result.refresh_token,
            "expires_in": result.expires_in, "token_type": result.token_type,
            "name": result.name,
        }, status_code=200)
    except Exception as e:
        return gen_error_response(e)


@auth_router.post("/resend-email", summary="Resends confirmation email",
    response_model=ResendConfirmationEmailResponse,
    responses={
        400: {"model": InvalidEmailFormatErrorResponse, "description": "Invalid email format, phone format, or password too weak"},
        409: {"model": EmailAlreadyInUseErrorResponse, "description": "Email or phone already in use"},
        500: {"model": RegisterResponse, "description": "Internal server error"},
    }, tags=["auth"])
def resend_email(input: ResendConfirmationEmailRequest):
    controller = _get_auth_controller()
    try:
        result = controller.resend_confirmation_email(input)
        return JSONResponse(content=result.model_dump(), status_code=201)
    except Exception as e:
        return gen_error_response(e)


@auth_router.post("/register", summary="Register new user with email and password",
    response_model=RegisterResponse,
    responses={
        400: {"model": InvalidEmailFormatErrorResponse, "description": "Invalid email format, phone format, or password too weak"},
        409: {"model": EmailAlreadyInUseErrorResponse, "description": "Email or phone already in use"},
        500: {"model": RegisterResponse, "description": "Internal server error"},
    }, tags=["auth"])
def register(input: RegisterRequest):
    controller = _get_auth_controller()
    try:
        result = controller.register(input)
        return JSONResponse(content={
            "user_id": result.user_id, "email": result.email, "message": result.message,
        }, status_code=201)
    except Exception as e:
        return gen_error_response(e)


@auth_router.post("/refresh", summary="Refresh access token using refresh token",
    response_model=RefreshTokenResponse,
    responses={
        401: {"model": TokenExpiredErrorResponse, "description": "Token expired or invalid"},
        500: {"model": RefreshTokenResponse, "description": "Internal server error"},
    }, tags=["auth"])
def refresh_token(input: RefreshTokenRequest):
    controller = _get_auth_controller()
    try:
        result = controller.refresh_token(input)
        return JSONResponse(content={
            "access_token": result.access_token, "refresh_token": result.refresh_token,
            "expires_in": result.expires_in, "token_type": result.token_type,
        }, status_code=200)
    except Exception as e:
        return gen_error_response(e)


@auth_router.post("/generate-api-key", summary="Generate API key for a user",
    response_model=GenApiKeyResponse, tags=["auth"])
def gen_api_key(input: GenApiKeyRequest):
    controller = _get_auth_controller()
    try:
        result = controller.generate_api_key(input)
        return JSONResponse(content={"api_key": result.api_key, "key_id": result.key_id}, status_code=201)
    except Exception as e:
        return gen_error_response(e)


@auth_router.post("/revoke-api-key", summary="Revokes an API key", tags=["auth"])
def revoke_api_key_(input: RevokeApiKeyRequest, user_id=Depends(get_user)):
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")
    controller = _get_auth_controller()
    try:
        result = controller.revoke_api_key(input)
        return JSONResponse(content=result, status_code=201)
    except Exception as e:
        return gen_error_response(e)


@auth_router.get("/list-api-keys/{user_id}", summary="List API keys for a user",
    tags=["auth"], response_model=List[ListApiKeyResponse])
def list_api_keys(user_id: str):
    if not user_id:
        raise HTTPException(status_code=401, detail="User id required")
    controller = _get_auth_controller()
    try:
        result = controller.list_api_keys(user_id=user_id)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        return gen_error_response(e)


@auth_router.get("/auth-info", summary="Get current authentication information",
    response_model=AuthMethodResponse, tags=["auth"])
def get_auth_info(user_id: str = Depends(get_user), authorization: Optional[str] = Header(None)):
    auth_service = _get_auth_service()
    try:
        auth_method = "api_key"
        if authorization and authorization.startswith("Bearer "):
            jwt_token = authorization[7:]
            user = PROVIDER.get_user_from_jwt(jwt_token)
            if user:
                auth_method = "jwt"
        user_email, user_name = auth_service.get_user_details(user_id)
        return AuthMethodResponse(method=auth_method, user_id=user_id, email=user_email, name=user_name)
    except Exception as e:
        return gen_error_response(e)


@auth_router.put("/update-profile", summary="Update user profile",
    response_model=UpdateUserResponse,
    responses={
        200: {"model": UpdateUserResponse, "description": "Profile updated successfully"},
        400: {"model": InvalidEmailFormatErrorResponse, "description": "Invalid input data"},
        401: {"model": InvalidTokenErrorResponse, "description": "Invalid or expired token"},
        500: {"model": UpdateUserResponse, "description": "Internal server error"},
    }, tags=["auth"])
def update_user_profile(request: UpdateUserRequest, user_id: str = Depends(get_user)):
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    controller = _get_auth_controller()
    try:
        result = controller.update_user_profile(user_id, request)
        return JSONResponse(content={
            "user_id": result.user_id, "email": result.email, "name": result.name,
            "phone": result.phone, "company": result.company, "message": result.message,
        }, status_code=200)
    except Exception as e:
        return gen_error_response(e)


@auth_router.post("/forgot-password", summary="Send password reset email",
    response_model=ForgotPasswordResponse,
    responses={
        200: {"model": ForgotPasswordResponse, "description": "Password reset email sent"},
        400: {"model": InvalidEmailFormatErrorResponse, "description": "Invalid email format"},
        500: {"model": ForgotPasswordResponse, "description": "Internal server error"},
    }, tags=["auth"])
def forgot_password(request: ForgotPasswordRequest):
    controller = _get_auth_controller()
    try:
        result = controller.forgot_password(request)
        return JSONResponse(content={"message": result.message}, status_code=200)
    except Exception as e:
        return gen_error_response(e)


@auth_router.post("/reset-password", summary="Reset password with access token",
    response_model=ResetPasswordResponse,
    responses={
        200: {"model": ResetPasswordResponse, "description": "Password reset successfully"},
        400: {"model": InvalidTokenErrorResponse, "description": "Invalid or expired token"},
        500: {"model": ResetPasswordResponse, "description": "Internal server error"},
    }, tags=["auth"])
def reset_password(request: ResetPasswordRequest):
    controller = _get_auth_controller()
    try:
        result = controller.reset_password(request)
        return JSONResponse(content={"message": result.message}, status_code=200)
    except Exception as e:
        return gen_error_response(e)