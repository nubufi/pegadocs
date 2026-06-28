from typing import Dict, List, Optional, Tuple

from loguru import logger

from app.application.exceptions import (
    ApiKeyGenerationException,
    ApiKeyListException,
    ApiKeyRevokeException,
    InvalidCredentialsException,
    LoginFailedException,
    RefreshTokenInvalidException,
    RegistrationFailedException,
    TokenRefreshFailedException,
)
from app.application.protocols.auth_provider import AuthProviderProtocol
from app.infra.auth_exception_mapper import map_supabase_error_to_exception


def normalize_email(email: str) -> str:
    return email.strip().lower()


class AuthService:
    def __init__(self, auth_provider: AuthProviderProtocol):
        self._provider = auth_provider

    def resend_confirmation_email(self, email: str) -> str:
        email = normalize_email(email)
        try:
            return self._provider.resend_confirmation_email(email)
        except Exception as e:
            logger.error(f"Resend confirmation email failed for {email}: {e}")
            raise map_supabase_error_to_exception(e, "resend_confirmation_email")

    def generate_api_key(self, user_id: str, expires_in_days: int, name: str) -> Tuple[str, Optional[str]]:
        try:
            return self._provider.generate_api_key(user_id, expires_in_days, name)
        except Exception as e:
            if isinstance(e, ApiKeyGenerationException):
                raise
            logger.error(f"Error generating API key for user_id={user_id}: {e}")
            raise ApiKeyGenerationException(f"Failed to generate API key: {str(e)}")

    def revoke_api_key(self, key_id: str) -> None:
        try:
            self._provider.revoke_api_key(key_id)
        except Exception as e:
            if isinstance(e, ApiKeyRevokeException):
                raise
            logger.error(f"Error revoking API key with key_id={key_id}: {e}")
            raise ApiKeyRevokeException(f"Failed to revoke API key: {str(e)}")

    def list_api_keys(self, user_id: str) -> List[Dict[str, any]]:
        try:
            return self._provider.list_api_keys(user_id)
        except Exception as e:
            if isinstance(e, ApiKeyListException):
                raise
            logger.error(f"Error listing API keys for user_id={user_id}: {e}")
            raise ApiKeyListException(f"Failed to list API keys: {str(e)}")

    def get_user_details(self, user_id: str) -> Tuple[str, Optional[str]]:
        try:
            return self._provider.get_user_details(user_id)
        except Exception as e:
            logger.error(f"Failed to fetch details for user_id={user_id}: {e}")
            raise map_supabase_error_to_exception(e, "get_user_details")

    def login(self, email: str, password: str) -> Tuple[str, str, str, int, Optional[str]]:
        email = normalize_email(email)
        try:
            return self._provider.login(email, password)
        except Exception as e:
            if isinstance(e, (InvalidCredentialsException, LoginFailedException)):
                raise
            logger.error(f"Login failed for email={email}: {e}")
            raise map_supabase_error_to_exception(e, "login")

    def register(self, email: str, password: str, name: str, phone: str,
                 company: Optional[str] = None) -> Tuple[str, str]:
        email = normalize_email(email)
        try:
            return self._provider.register(email, password, name, phone, company)
        except Exception as e:
            if isinstance(e, RegistrationFailedException):
                raise
            logger.error(f"Registration failed for email={email}: {e}")
            raise map_supabase_error_to_exception(e, "register")

    def refresh_token(self, refresh_token: str) -> Tuple[str, str, int]:
        try:
            return self._provider.refresh_token(refresh_token)
        except Exception as e:
            if isinstance(e, (TokenRefreshFailedException, RefreshTokenInvalidException)):
                raise
            logger.error(f"Token refresh failed: {e}")
            raise map_supabase_error_to_exception(e, "refresh")

    def logout(self, access_token: str) -> bool:
        logger.info("Attempting logout")
        try:
            logger.info("Logout successful")
            return True
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            raise Exception(f"Logout failed: {str(e)}")

    def update_user_profile(self, user_id: str, name: Optional[str] = None,
                            phone: Optional[str] = None, company: Optional[str] = None) -> Tuple[str, str, str, str, Optional[str]]:
        try:
            return self._provider.update_user_profile(user_id, name, phone, company)
        except Exception as e:
            logger.error(f"Profile update failed for user_id={user_id}: {e}")
            raise map_supabase_error_to_exception(e, "update_profile")

    def forgot_password(self, email: str) -> str:
        email = normalize_email(email)
        try:
            return self._provider.forgot_password(email)
        except Exception as e:
            logger.error(f"Password reset email failed for {email}: {e}")
            raise map_supabase_error_to_exception(e, "forgot_password")

    def reset_password(self, access_token: str, new_password: str) -> str:
        try:
            return self._provider.reset_password(access_token, new_password)
        except Exception as e:
            logger.error(f"Password reset failed: {e}")
            raise map_supabase_error_to_exception(e, "reset_password")