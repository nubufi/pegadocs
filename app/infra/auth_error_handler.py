"""
Custom error handler for authentication exceptions.
"""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.application.exceptions import (
    AccountLockedException,
    AuthenticationException,
    EmailAlreadyInUseException,
    EmailVerificationRequiredException,
    InvalidCredentialsException,
    InvalidEmailFormatException,
    InvalidPhoneFormatException,
    InvalidTokenException,
    PasswordTooWeakException,
    PhoneAlreadyInUseException,
    RefreshTokenInvalidException,
    RegistrationFailedException,
    SessionExpiredException,
    TokenExpiredException,
    UnknownAuthenticationException,
    UserAccountDisabledException,
    UserNotVerifiedException,
)


def get_auth_error_response(exception: AuthenticationException) -> JSONResponse:
    """
    Convert authentication exception to appropriate HTTP response.

    Args:
        exception (AuthenticationException): The authentication exception

    Returns:
        JSONResponse: The appropriate HTTP response
    """
    # Map exceptions to HTTP status codes and error details
    error_mappings = {
        # 400 Bad Request
        InvalidEmailFormatException: (
            status.HTTP_400_BAD_REQUEST,
            "INVALID_EMAIL_FORMAT",
        ),
        InvalidPhoneFormatException: (
            status.HTTP_400_BAD_REQUEST,
            "INVALID_PHONE_FORMAT",
        ),
        PasswordTooWeakException: (status.HTTP_400_BAD_REQUEST, "PASSWORD_TOO_WEAK"),
        # 401 Unauthorized
        InvalidCredentialsException: (
            status.HTTP_401_UNAUTHORIZED,
            "INVALID_CREDENTIALS",
        ),
        InvalidTokenException: (status.HTTP_401_UNAUTHORIZED, "INVALID_TOKEN"),
        TokenExpiredException: (status.HTTP_401_UNAUTHORIZED, "TOKEN_EXPIRED"),
        RefreshTokenInvalidException: (
            status.HTTP_401_UNAUTHORIZED,
            "INVALID_REFRESH_TOKEN",
        ),
        SessionExpiredException: (status.HTTP_401_UNAUTHORIZED, "SESSION_EXPIRED"),
        # 403 Forbidden
        UserAccountDisabledException: (status.HTTP_403_FORBIDDEN, "ACCOUNT_DISABLED"),
        AccountLockedException: (status.HTTP_403_FORBIDDEN, "ACCOUNT_LOCKED"),
        UserNotVerifiedException: (status.HTTP_403_FORBIDDEN, "EMAIL_NOT_VERIFIED"),
        EmailVerificationRequiredException: (
            status.HTTP_403_FORBIDDEN,
            "EMAIL_VERIFICATION_REQUIRED",
        ),
        # 409 Conflict
        EmailAlreadyInUseException: (status.HTTP_409_CONFLICT, "EMAIL_ALREADY_IN_USE"),
        PhoneAlreadyInUseException: (status.HTTP_409_CONFLICT, "PHONE_ALREADY_IN_USE"),
        # 500 Internal Server Error
        RegistrationFailedException: (
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "REGISTRATION_FAILED",
        ),
        UnknownAuthenticationException: (
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "UNKNOWN_AUTH_ERROR",
        ),
    }

    # Get the appropriate status code and error code
    status_code, error_code = error_mappings.get(
        type(exception), (status.HTTP_500_INTERNAL_SERVER_ERROR, "UNKNOWN_ERROR")
    )

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": error_code,
                "message": str(exception),
                "type": exception.__class__.__name__,
            }
        },
    )


async def auth_exception_handler(
    request: Request, exc: AuthenticationException
) -> JSONResponse:
    """
    FastAPI exception handler for authentication exceptions.

    Args:
        request (Request): The FastAPI request
        exc (AuthenticationException): The authentication exception

    Returns:
        JSONResponse: The appropriate HTTP response
    """
    return get_auth_error_response(exc)
