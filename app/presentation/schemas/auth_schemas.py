from typing import Optional
from pydantic import BaseModel


class GenApiKeyRequest(BaseModel):
    user_id: str
    expires_in_days: int = 30
    name: str

class GenApiKeyResponse(BaseModel):
    api_key: str
    key_id: str

class ListApiKeyResponse(BaseModel):
    key_id: str
    created_at: str
    expires_at: str
    name: str

class RevokeApiKeyRequest(BaseModel):
    key_id: str

class AuthMethodResponse(BaseModel):
    method: str  # "jwt" or "api_key"
    user_id: str
    email: str
    name: Optional[str] = None

class ResendConfirmationEmailRequest(BaseModel):
    email: str

class ResendConfirmationEmailResponse(BaseModel):
    message: str = "Confirmation email resent. Please check your inbox."

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    phone: str
    company: Optional[str] = ""

class AuthResponse(BaseModel):
    user_id: str
    email: str
    name: Optional[str] = None
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "bearer"

class RegisterResponse(BaseModel):
    user_id: str
    email: str
    message: str = "Registration successful. Please check your email to verify your account."

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "bearer"

# ==================== ERROR RESPONSE SCHEMAS ====================

class AuthErrorDetail(BaseModel):
    code: str
    message: str
    type: str

class AuthErrorResponse(BaseModel):
    error: AuthErrorDetail

class EmailAlreadyInUseErrorResponse(BaseModel):
    error: AuthErrorDetail = AuthErrorDetail(
        code="EMAIL_ALREADY_IN_USE", message="Email address is already in use",
        type="EmailAlreadyInUseException")

class PhoneAlreadyInUseErrorResponse(BaseModel):
    error: AuthErrorDetail = AuthErrorDetail(
        code="PHONE_ALREADY_IN_USE", message="Phone number is already in use",
        type="PhoneAlreadyInUseException")

class InvalidCredentialsErrorResponse(BaseModel):
    error: AuthErrorDetail = AuthErrorDetail(
        code="INVALID_CREDENTIALS", message="Invalid email or password",
        type="InvalidCredentialsException")

class EmailNotVerifiedErrorResponse(BaseModel):
    error: AuthErrorDetail = AuthErrorDetail(
        code="EMAIL_NOT_VERIFIED", message="Email verification required",
        type="UserNotVerifiedException")

class PasswordTooWeakErrorResponse(BaseModel):
    error: AuthErrorDetail = AuthErrorDetail(
        code="PASSWORD_TOO_WEAK", message="Password does not meet security requirements",
        type="PasswordTooWeakException")

class InvalidEmailFormatErrorResponse(BaseModel):
    error: AuthErrorDetail = AuthErrorDetail(
        code="INVALID_EMAIL_FORMAT", message="Invalid email format",
        type="InvalidEmailFormatException")

class InvalidPhoneFormatErrorResponse(BaseModel):
    error: AuthErrorDetail = AuthErrorDetail(
        code="INVALID_PHONE_FORMAT", message="Invalid phone number format",
        type="InvalidPhoneFormatException")

class TokenExpiredErrorResponse(BaseModel):
    error: AuthErrorDetail = AuthErrorDetail(
        code="TOKEN_EXPIRED", message="Token has expired", type="TokenExpiredException")

class InvalidTokenErrorResponse(BaseModel):
    error: AuthErrorDetail = AuthErrorDetail(
        code="INVALID_TOKEN", message="Invalid or expired token", type="InvalidTokenException")

class AccountLockedErrorResponse(BaseModel):
    error: AuthErrorDetail = AuthErrorDetail(
        code="ACCOUNT_LOCKED", message="Account is locked due to security reasons",
        type="AccountLockedException")

class AccountDisabledErrorResponse(BaseModel):
    error: AuthErrorDetail = AuthErrorDetail(
        code="ACCOUNT_DISABLED", message="Account is disabled",
        type="UserAccountDisabledException")

# User Profile Management Schemas
class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None

class UpdateUserResponse(BaseModel):
    user_id: str
    email: str
    name: str
    phone: str
    company: Optional[str] = None
    message: str = "User profile updated successfully."

# Password Reset Schemas
class ForgotPasswordRequest(BaseModel):
    email: str

class ForgotPasswordResponse(BaseModel):
    message: str = "Password reset email sent. Please check your inbox."

class ResetPasswordRequest(BaseModel):
    access_token: str
    new_password: str

class ResetPasswordResponse(BaseModel):
    message: str = "Password reset successfully. You can now log in with your new password."