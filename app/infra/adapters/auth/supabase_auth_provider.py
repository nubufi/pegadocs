from typing import Any, Dict, List, Optional, Tuple

from loguru import logger

from app.application.exceptions import (
    ApiKeyGenerationException,
    ApiKeyListException,
    ApiKeyRevokeException,
    InvalidCredentialsException,
)
from app.infra.auth import _get_supabase


def normalize_email(email: str) -> str:
    return email.strip().lower()


class SupabaseAuthProvider:
    def __init__(self):
        pass

    def login(self, email: str, password: str) -> Tuple[str, str, str, int, Optional[str]]:
        email = normalize_email(email)
        logger.info(f"Attempting login for email={email}")
        response = _get_supabase().auth.sign_in_with_password({"email": email, "password": password})
        if response.user and response.session:
            user_id = response.user.id
            access_token = response.session.access_token
            refresh_token = response.session.refresh_token
            expires_in = response.session.expires_in
            user_metadata = response.user.user_metadata or {}
            name = user_metadata.get("name")
            logger.info(f"Login successful for user_id={user_id}")
            return user_id, access_token, refresh_token, expires_in, name
        logger.warning(f"Login failed for email={email}: Invalid response")
        raise InvalidCredentialsException("Invalid email or password")

    def register(self, email: str, password: str, name: str, phone: str,
                 company: Optional[str] = None) -> Tuple[str, str]:
        from app.application.exceptions import EmailAlreadyInUseException, RegistrationFailedException

        email = normalize_email(email)
        logger.info(f"Attempting registration for email={email}")

        try:
            page = 1
            per_page = 50
            while True:
                users = _get_supabase().auth.admin.list_users(page=page, per_page=per_page)
                if not users:
                    break
                for user in users:
                    if user.email and user.email.lower() == email.lower():
                        raise EmailAlreadyInUseException("Email address is already in use")
                if len(users) < per_page:
                    break
                page += 1
        except EmailAlreadyInUseException:
            raise
        except Exception as e:
            logger.warning(f"Could not check for existing users: {e}")

        signup_data: dict = {"email": email, "password": password}
        user_metadata = {"name": name, "phone": phone}
        if company:
            user_metadata["company"] = company
        signup_data["options"] = {"data": user_metadata}
        response = _get_supabase().auth.sign_up(signup_data)
        if response.user:
            user_id = response.user.id
            if response.session:
                logger.info(f"Registration successful with session for user_id={user_id}")
                return user_id, "Registration successful. You are now logged in."
            logger.info(f"Registration successful, email validation required for user_id={user_id}")
            return user_id, "Registration successful. Please check your email to verify your account."
        logger.warning(f"Registration failed for email={email}: Invalid response")
        raise RegistrationFailedException("Invalid registration response")

    def refresh_token(self, refresh_token: str) -> Tuple[str, str, int]:
        logger.info("Attempting token refresh")
        response = _get_supabase().auth.refresh_session(refresh_token)
        if response.session:
            access_token = response.session.access_token
            new_refresh_token = response.session.refresh_token
            expires_in = response.session.expires_in
            logger.info("Token refresh successful")
            return access_token, new_refresh_token, expires_in
        logger.warning("Token refresh failed: Invalid response")
        from app.application.exceptions import TokenRefreshFailedException
        raise TokenRefreshFailedException("Invalid refresh response")

    def get_user_details(self, user_id: str) -> Tuple[str, Optional[str]]:
        logger.info(f"Fetching details for user_id={user_id}")
        from app.infra.auth import get_supabase_client

        client = get_supabase_client()
        response = client.auth.admin.get_user_by_id(user_id)
        if response and response.user and response.user.email:
            user_metadata = response.user.user_metadata or {}
            name = user_metadata.get("name")
            return response.user.email, name
        raise Exception("User not found")

    def update_user_profile(self, user_id: str, name: Optional[str] = None,
                            phone: Optional[str] = None, company: Optional[str] = None) -> Tuple[str, str, str, str, Optional[str]]:
        logger.info(f"Attempting to update profile for user_id={user_id}")
        current_user = _get_supabase().auth.admin.get_user_by_id(user_id)
        if not current_user or not current_user.user:
            raise Exception("User not found")
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if phone is not None:
            update_data["phone"] = phone
        if company is not None:
            update_data["company"] = company
        if not update_data:
            user_metadata = current_user.user.user_metadata or {}
            return (user_id, current_user.user.email or "",
                    user_metadata.get("name", ""), user_metadata.get("phone", ""),
                    user_metadata.get("company"))
        response = _get_supabase().auth.admin.update_user_by_id(user_id, {"user_metadata": update_data})
        if response and response.user:
            user_metadata = response.user.user_metadata or {}
            logger.info(f"Profile updated successfully for user_id={user_id}")
            return (user_id, response.user.email or "",
                    user_metadata.get("name", ""), user_metadata.get("phone", ""),
                    user_metadata.get("company"))
        raise Exception("Failed to update user profile")

    def forgot_password(self, email: str) -> str:
        email = normalize_email(email)
        logger.info(f"Attempting to send password reset email to {email}")
        response = _get_supabase().auth.reset_password_email(email)
        if response:
            logger.info(f"Password reset email sent successfully to {email}")
            return "Password reset email sent. Please check your inbox."
        raise Exception("Failed to send password reset email")

    def reset_password(self, access_token: str, new_password: str) -> str:
        logger.info("Attempting to reset password")
        response = _get_supabase().auth.update_user({"password": new_password}, access_token=access_token)
        if response and response.user:
            logger.info("Password reset successfully")
            return "Password reset successfully. You can now log in with your new password."
        raise Exception("Failed to reset password")

    def resend_confirmation_email(self, email: str) -> str:
        email = normalize_email(email)
        logger.info(f"Attempting to resend confirmation email to {email}")
        response = _get_supabase().auth.resend({"email": email, "type": "signup"})
        if response:
            logger.info(f"Confirmation email resent successfully to {email}")
            return "Confirmation email resent. Please check your inbox."
        raise Exception("Failed to resend confirmation email")

    def generate_api_key(self, user_id: str, expires_in_days: int, name: str) -> Tuple[str, str]:
        from app.infra.auth import create_api_key

        logger.info(f"Generating API key for user_id={user_id}, expires_in_days={expires_in_days}")
        try:
            api_key, key_id = create_api_key(user_id, expires_in_days, name)
            logger.debug(f"API key generated successfully with key_id={key_id}")
            return api_key, key_id
        except Exception as e:
            logger.error(f"Error generating API key for user_id={user_id}: {e}")
            raise ApiKeyGenerationException(f"Failed to generate API key: {str(e)}")

    def revoke_api_key(self, key_id: str) -> None:
        from app.infra.auth import revoke_api_key as supabase_revoke_api_key

        logger.info(f"Revoking API key with key_id={key_id}")
        try:
            supabase_revoke_api_key(key_id)
            logger.debug(f"API key with key_id={key_id} successfully revoked")
        except Exception as e:
            logger.error(f"Error revoking API key with key_id={key_id}: {e}")
            raise ApiKeyRevokeException(f"Failed to revoke API key: {str(e)}")

    def list_api_keys(self, user_id: str) -> List[Dict[str, Any]]:
        from app.infra.auth import list_api_keys as supabase_list_api_keys

        logger.info(f"Listing API keys for user_id={user_id}")
        try:
            api_keys = supabase_list_api_keys(user_id)
            logger.debug(f"Found {len(api_keys)} API keys for user_id={user_id}")
            return api_keys
        except Exception as e:
            logger.error(f"Error listing API keys for user_id={user_id}: {e}")
            raise ApiKeyListException(f"Failed to list API keys: {str(e)}")

    def get_user_from_jwt(self, token: str) -> Optional[Any]:
        from app.infra.auth import get_user_from_jwt as supabase_get_user_from_jwt

        return supabase_get_user_from_jwt(token)

    def get_user_from_api_key(self, api_key: str) -> Optional[str]:
        from app.infra.auth import get_user_from_api_key as supabase_get_user_from_api_key

        return supabase_get_user_from_api_key(api_key)