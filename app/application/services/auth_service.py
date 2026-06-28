from typing import Any, Dict, List, Optional, Tuple

from app.application.services.referal_service import ReferalService
from loguru import logger

from app.application.exceptions import (
    ApiKeyGenerationException,
    ApiKeyListException,
    ApiKeyRevokeException,
    EmailAlreadyInUseException,
    InvalidCredentialsException,
    LoginFailedException,
    RefreshTokenInvalidException,
    RegistrationFailedException,
    TokenRefreshFailedException,
)
from app.infra.auth import (
    create_api_key,
    list_api_keys,
    revoke_api_key,
    supabase,
    get_supabase_client,
)
from app.infra.auth_exception_mapper import map_supabase_error_to_exception


def normalize_email(email: str) -> str:
    """
    Normalize email address by converting to lowercase and trimming whitespace.
    Args:
        email (str): The email address to normalize
    Returns:
        str: The normalized email address
    """
    return email.strip().lower()


class AuthService:
    """Business logic for authentication operations"""

    referal_service = ReferalService()

    def resend_confirmation_email(self, email: str) -> str:
        """
        Resend confirmation email to user.
        Returns: Success message
        """
        # Normalize email address
        email = normalize_email(email)
        logger.info(f"Attempting to resend confirmation email to {email}")

        try:
            response = supabase.auth.resend({"email": email, "type": "signup"})

            if response:
                logger.info(f"Confirmation email resent successfully to {email}")
                return "Confirmation email resent. Please check your inbox."
            else:
                raise Exception("Failed to resend confirmation email")

        except Exception as e:
            logger.error(f"Resend confirmation email failed for {email}: {e}")
            raise map_supabase_error_to_exception(e, "resend_confirmation_email")

    def generate_api_key(
        self, user_id: str, expires_in_days: int, name: str
    ) -> tuple[str, str | None]:
        """
        Generate an API key for a user in a project
        """
        logger.info(
            f"Generating API key for user_id={user_id}, expires_in_days={expires_in_days}"
        )
        try:
            api_key, key_id = create_api_key(user_id, expires_in_days, name)
            logger.debug(f"API key generated successfully with key_id={key_id}")
            return api_key, key_id
        except Exception as e:
            logger.error(f"Error generating API key for user_id={user_id}: {e}")
            raise ApiKeyGenerationException(f"Failed to generate API key: {str(e)}")

    def revoke_api_key(self, key_id: str) -> None:
        """
        Revoke an API key by its ID
        """
        logger.info(f"Revoking API key with key_id={key_id}")
        try:
            revoke_api_key(key_id)
            logger.debug(f"API key with key_id={key_id} successfully revoked")
        except Exception as e:
            logger.error(f"Error revoking API key with key_id={key_id}: {e}")
            raise ApiKeyRevokeException(f"Failed to revoke API key: {str(e)}")

    def list_api_keys(self, user_id: str) -> List[Dict[str, Any]]:
        """
        List all API keys for a user in a project
        """
        logger.info(f"Listing API keys for user_id={user_id}")
        try:
            api_keys = list_api_keys(user_id)
            logger.debug(f"Found {len(api_keys)} API keys for user_id={user_id}")
            return api_keys
        except Exception as e:
            logger.error(f"Error listing API keys for user_id={user_id}: {e}")
            raise ApiKeyListException(f"Failed to list API keys: {str(e)}")

    def get_user_details(self, user_id: str) -> Tuple[str, Optional[str]]:
        """
        Retrieve the user's email address and name by their ID.
        """
        logger.info(f"Fetching details for user_id={user_id}")
        try:
            client = get_supabase_client()
            response = client.auth.admin.get_user_by_id(user_id)
            if response and response.user and response.user.email:
                user_metadata = response.user.user_metadata or {}
                name = user_metadata.get("name")
                return response.user.email, name
            raise Exception("User not found")
        except Exception as e:
            logger.error(f"Failed to fetch details for user_id={user_id}: {e}")
            raise map_supabase_error_to_exception(e, "get_user_details")

    def login(self, email: str, password: str) -> Tuple[str, str, str, int, Optional[str]]:
        """
        Login user with email and password using Supabase auth.
        Returns: (user_id, access_token, refresh_token, expires_in, name)
        """
        # Normalize email address
        email = normalize_email(email)
        logger.info(f"Attempting login for email={email}")
        try:
            response = supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )

            if response.user and response.session:
                user_id = response.user.id
                access_token = response.session.access_token
                refresh_token = response.session.refresh_token
                expires_in = response.session.expires_in
                
                user_metadata = response.user.user_metadata or {}
                name = user_metadata.get("name")

                logger.info(f"Login successful for user_id={user_id}")
                return user_id, access_token, refresh_token, expires_in, name
            else:
                logger.warning(f"Login failed for email={email}: Invalid response")
                raise InvalidCredentialsException("Invalid email or password")

        except Exception as e:
            logger.error(f"Login failed for email={email}: {e}")
            # Map Supabase errors to custom exceptions
            if isinstance(e, (InvalidCredentialsException, LoginFailedException)):
                raise
            else:
                raise map_supabase_error_to_exception(e, "login")

    def _check_user_exists(self, email: str) -> None:
        """
        Check if a user with the same email already exists using admin API.
        Raises EmailAlreadyInUseException if duplicate is found.
        """
        try:
            # Check for existing email using admin API with pagination
            page = 1
            per_page = 50  # Adjust page size as needed
            
            while True:
                # Fetch users for the current page
                users = supabase.auth.admin.list_users(page=page, per_page=per_page)
                
                if not users:
                    break
                
                # Check for the email in the current page
                for user in users:
                    if user.email and user.email.lower() == email.lower():
                        raise EmailAlreadyInUseException(
                            "Email address is already in use"
                        )
                
                # If fewer users than per_page are returned, we've reached the last page
                if len(users) < per_page:
                    break
                
                page += 1

        except EmailAlreadyInUseException:
            raise
        except Exception as e:
            logger.warning(f"Could not check for existing users: {e}")
            # Continue with registration if we can't check - Supabase will handle duplicates

    def register(
        self,
        email: str,
        password: str,
        name: str,
        phone: str,
        reference_code: Optional[str] = None,
        company: Optional[str] = None,
    ) -> Tuple[str, str]:
        """
        Register new user with email and password using Supabase auth.
        Returns: (user_id, message) - no tokens when email validation is required
        """
        # Normalize email address
        email = normalize_email(email)
        logger.info(f"Attempting registration for email={email}")

        try:
            # Check if user already exists
            self._check_user_exists(email)

            signup_data: dict = {"email": email, "password": password}

            # Build user metadata from individual fields
            user_metadata = {"name": name, "phone": phone}

            if reference_code:
                user_metadata["reference_code"] = reference_code
            if company:
                user_metadata["company"] = company

            signup_data["options"] = {"data": user_metadata}

            response = supabase.auth.sign_up(signup_data)

            if response.user:
                user_id = response.user.id
                self.referal_service.add_reference_code(user_id)

                # Check if session is available (email validation disabled)
                if response.session:
                    logger.info(
                        f"Registration successful with session for user_id={user_id}"
                    )
                    return user_id, "Registration successful. You are now logged in."
                else:
                    # Email validation is required, no session returned
                    logger.info(
                        f"Registration successful, email validation required for user_id={user_id}"
                    )
                    return (
                        user_id,
                        "Registration successful. Please check your email to verify your account.",
                    )
            else:
                logger.warning(
                    f"Registration failed for email={email}: Invalid response"
                )
                raise RegistrationFailedException("Invalid registration response")

        except Exception as e:
            logger.error(f"Registration failed for email={email}: {e}")
            # Map Supabase errors to custom exceptions
            if isinstance(
                e,
                (
                    RegistrationFailedException,
                    EmailAlreadyInUseException,
                ),
            ):
                raise
            else:
                # Let the exception mapper handle Supabase's built-in duplicate detection
                mapped_exception = map_supabase_error_to_exception(e, "register")
                raise mapped_exception

    def refresh_token(self, refresh_token: str) -> Tuple[str, str, int]:
        """
        Refresh access token using refresh token.
        Returns: (access_token, refresh_token, expires_in)
        """
        logger.info("Attempting token refresh")
        try:
            response = supabase.auth.refresh_session(refresh_token)

            if response.session:
                access_token = response.session.access_token
                new_refresh_token = response.session.refresh_token
                expires_in = response.session.expires_in

                logger.info("Token refresh successful")
                return access_token, new_refresh_token, expires_in
            else:
                logger.warning("Token refresh failed: Invalid response")
                raise Exception("Invalid refresh response")

        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            # Map Supabase errors to custom exceptions
            if isinstance(
                e, (TokenRefreshFailedException, RefreshTokenInvalidException)
            ):
                raise
            else:
                raise map_supabase_error_to_exception(e, "refresh")

    def logout(self, access_token: str) -> bool:
        """
        Logout user by invalidating the session.
        """
        logger.info("Attempting logout")
        try:
            response = supabase.auth.sign_out()
            logger.info("Logout successful")
            return True
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            raise Exception(f"Logout failed: {str(e)}")

    def update_user_profile(
        self,
        user_id: str,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        company: Optional[str] = None,
        reference_code: Optional[str] = None,
    ) -> Tuple[str, str, str, str, Optional[str], Optional[str]]:
        """
        Update user profile information.
        Returns: (user_id, email, name, phone, company, reference_code)
        """
        logger.info(f"Attempting to update profile for user_id={user_id}")
        try:
            # Get current user data
            current_user = supabase.auth.admin.get_user_by_id(user_id)
            if not current_user or not current_user.user:
                raise Exception("User not found")

            # Build update data
            update_data = {}
            if name is not None:
                update_data["name"] = name
            if phone is not None:
                update_data["phone"] = phone
            if company is not None:
                update_data["company"] = company
            if reference_code is not None:
                update_data["reference_code"] = reference_code

            if not update_data:
                # No changes to make, return current data
                user_metadata = current_user.user.user_metadata or {}
                return (
                    user_id,
                    current_user.user.email or "",
                    user_metadata.get("name", ""),
                    user_metadata.get("phone", ""),
                    user_metadata.get("company"),
                    user_metadata.get("reference_code"),
                )

            # Update user metadata
            response = supabase.auth.admin.update_user_by_id(
                user_id, {"user_metadata": update_data}
            )

            if response and response.user:
                user_metadata = response.user.user_metadata or {}
                logger.info(f"Profile updated successfully for user_id={user_id}")
                return (
                    user_id,
                    response.user.email or "",
                    user_metadata.get("name", ""),
                    user_metadata.get("phone", ""),
                    user_metadata.get("company"),
                    user_metadata.get("reference_code"),
                )
            else:
                raise Exception("Failed to update user profile")

        except Exception as e:
            logger.error(f"Profile update failed for user_id={user_id}: {e}")
            raise map_supabase_error_to_exception(e, "update_profile")

    def forgot_password(self, email: str) -> str:
        """
        Send password reset email to user.
        Returns: Success message
        """
        # Normalize email address
        email = normalize_email(email)
        logger.info(f"Attempting to send password reset email to {email}")

        try:
            response = supabase.auth.reset_password_email(email)

            if response:
                logger.info(f"Password reset email sent successfully to {email}")
                return "Password reset email sent. Please check your inbox."
            else:
                raise Exception("Failed to send password reset email")

        except Exception as e:
            logger.error(f"Password reset email failed for {email}: {e}")
            raise map_supabase_error_to_exception(e, "forgot_password")

    def reset_password(self, access_token: str, new_password: str) -> str:
        """
        Reset user password using access token from reset email.
        Returns: Success message
        """
        logger.info("Attempting to reset password")
        try:
            # Update password using the access token
            response = supabase.auth.update_user(
                {"password": new_password}, access_token=access_token
            )

            if response and response.user:
                logger.info("Password reset successfully")
                return "Password reset successfully. You can now log in with your new password."
            else:
                raise Exception("Failed to reset password")

        except Exception as e:
            logger.error(f"Password reset failed: {e}")
            raise map_supabase_error_to_exception(e, "reset_password")
