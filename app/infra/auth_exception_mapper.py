"""
Authentication exception mapper for converting Supabase errors to custom exceptions.
"""

from app.application.exceptions import (
    AccountLockedException,
    EmailAlreadyInUseException,
    EmailVerificationRequiredException,
    InvalidCredentialsException,
    InvalidEmailFormatException,
    InvalidPhoneFormatException,
    InvalidTokenException,
    LoginFailedException,
    PasswordTooWeakException,
    RefreshTokenInvalidException,
    RegistrationFailedException,
    SessionExpiredException,
    TokenExpiredException,
    TokenRefreshFailedException,
    UnknownAuthenticationException,
    UserAccountDisabledException,
    UserNotVerifiedException,
)


def map_supabase_auth_error(
    error_message: str, operation: str = "authentication"
) -> Exception:
    """
    Map Supabase authentication error messages to custom exceptions.

    Args:
        error_message (str): The error message from Supabase
        operation (str): The operation being performed (login, register, etc.)

    Returns:
        Exception: The appropriate custom exception
    """
    error_lower = error_message.lower()

    # Email-related errors
    if "email" in error_lower and (
        "already" in error_lower or "exists" in error_lower or "taken" in error_lower
    ):
        return EmailAlreadyInUseException("Email address is already in use")

    if "email" in error_lower and ("invalid" in error_lower or "format" in error_lower):
        return InvalidEmailFormatException("Invalid email format")

    # User already exists errors
    if "user" in error_lower and ("already" in error_lower or "exists" in error_lower):
        return EmailAlreadyInUseException("User with this email already exists")

    # Common Supabase error patterns
    if "signup" in error_lower and "disabled" in error_lower:
        return RegistrationFailedException("User registration is disabled")

    if "signup" in error_lower and "email" in error_lower and "confirm" in error_lower:
        return EmailAlreadyInUseException("Email address is already registered")

    # Generic duplicate detection
    if "duplicate" in error_lower or "already registered" in error_lower:
        return EmailAlreadyInUseException("Email address is already in use")

    # Phone-related errors (removed - no longer checking phone uniqueness)
    # if "phone" in error_lower and "already" in error_lower:
    #     return PhoneAlreadyInUseException("Phone number is already in use")

    if "phone" in error_lower and ("invalid" in error_lower or "format" in error_lower):
        return InvalidPhoneFormatException("Invalid phone number format")

    # Password-related errors
    if "password" in error_lower and (
        "weak" in error_lower or "strength" in error_lower
    ):
        return PasswordTooWeakException("Password does not meet security requirements")

    if "password" in error_lower and (
        "invalid" in error_lower or "incorrect" in error_lower
    ):
        return InvalidCredentialsException("Invalid email or password")

    # Token-related errors
    if "token" in error_lower and (
        "invalid" in error_lower or "malformed" in error_lower
    ):
        return InvalidTokenException("Invalid or malformed token")

    if "token" in error_lower and ("expired" in error_lower or "expire" in error_lower):
        return TokenExpiredException("Token has expired")

    if "refresh" in error_lower and "token" in error_lower:
        return RefreshTokenInvalidException("Invalid or expired refresh token")

    # User account status errors
    if "email" in error_lower and ("confirm" in error_lower or "verify" in error_lower):
        return EmailVerificationRequiredException("Email verification required")

    if "account" in error_lower and (
        "disabled" in error_lower or "deactivated" in error_lower
    ):
        return UserAccountDisabledException("Account is disabled")

    if "account" in error_lower and (
        "locked" in error_lower or "suspended" in error_lower
    ):
        return AccountLockedException("Account is locked due to security reasons")

    if "user" in error_lower and (
        "not found" in error_lower or "doesn't exist" in error_lower
    ):
        return InvalidCredentialsException("Invalid email or password")

    # Session-related errors
    if "session" in error_lower and (
        "expired" in error_lower or "invalid" in error_lower
    ):
        return SessionExpiredException("Session has expired")

    # Rate limiting
    if "rate" in error_lower and "limit" in error_lower:
        return AccountLockedException("Too many attempts. Please try again later")

    # Network/connection errors
    if (
        "network" in error_lower
        or "connection" in error_lower
        or "timeout" in error_lower
    ):
        return UnknownAuthenticationException("Network error. Please try again")

    # Operation-specific fallbacks
    if operation == "login":
        return LoginFailedException(f"Login failed: {error_message}")
    elif operation == "register":
        return RegistrationFailedException(f"Registration failed: {error_message}")
    elif operation == "refresh":
        return TokenRefreshFailedException(f"Token refresh failed: {error_message}")
    else:
        return UnknownAuthenticationException(f"Authentication error: {error_message}")


def map_supabase_error_to_exception(
    supabase_error: Exception, operation: str = "authentication"
) -> Exception:
    """
    Map a Supabase exception to a custom authentication exception.

    Args:
        supabase_error (Exception): The exception from Supabase
        operation (str): The operation being performed

    Returns:
        Exception: The appropriate custom exception
    """
    error_message = str(supabase_error)
    return map_supabase_auth_error(error_message, operation)
