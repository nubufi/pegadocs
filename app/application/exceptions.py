class ApplicationException(Exception):
    """Base exception for application layer"""

    pass


class CollectionCreationException(ApplicationException):
    """Raised when a collection cannot be created"""

    pass


class CollectionDeletionException(ApplicationException):
    """Raised when a collection cannot be deleted"""

    pass


class CollectionListException(ApplicationException):
    """Raised when collections cannot be listed"""

    pass


class CollectionNotFoundException(ApplicationException):
    """Raised when a collection is not found"""

    pass


class DataSourceCreationException(ApplicationException):
    """Raised when a data source cannot be created"""

    pass


class DataSourceUpdateException(ApplicationException):
    """Raised when a data source cannot be deleted"""

    pass


class DataSourceDeletionException(ApplicationException):
    """Raised when a data source cannot be deleted"""

    pass


class DataSourceListException(ApplicationException):
    """Raised when data sources cannot be listed"""

    pass


class DataSourceNotFoundException(ApplicationException):
    """Raised when a data source is not found"""

    pass


class ChatFailedException(ApplicationException):
    """Raised when a chat operation fails"""

    pass


class ChatNotFoundException(ApplicationException):
    """Raised when a chat is not found"""

    pass


class ChatMetadataAddException(ApplicationException):
    """Raised when chat metadata cannot be added"""

    pass


class ChatDeleteException(ApplicationException):
    """Raised when chat or its history cannot be deleted"""

    pass


class ChatMetadataFetchException(ApplicationException):
    """Raised when chat metadata fetch fails"""

    pass


class UserNotFoundException(ApplicationException):
    """Raised when a user is not found"""

    pass


class ApiKeyGenerationException(ApplicationException):
    """Raised when an API key cannot be generated"""

    pass


class ApiKeyRevokeException(ApplicationException):
    """Raised when an API key cannot be revoked"""

    pass


class ApiKeyListException(ApplicationException):
    """Raised when API keys cannot be listed"""

    pass


class ApiKeyNotFoundException(ApplicationException):
    """Raised when an API key is not found"""

    pass


class InvalidRequestException(ApplicationException):
    """Raised when the request data is invalid"""

    pass


class OperationFailedException(ApplicationException):
    """Raised when an operation fails"""

    pass


class DatabaseIndexCreationException(ApplicationException):
    """Raised when a database index cannot be created"""

    pass


class DatabaseIndexDeletionException(ApplicationException):
    """Raised when a database index cannot be deleted"""

    pass


class DatabaseIndexUpdateException(ApplicationException):
    """Raised when a database index cannot be updated"""

    pass


class DatabaseIndexListException(ApplicationException):
    """Raised when database indexes cannot be listed"""

    pass


class DatabaseIndexNotFoundException(ApplicationException):
    """Raised when a database index is not found"""

    pass


class SASUrlGenerationException(ApplicationException):
    """Raised when a SAS URL cannot be generated"""

    pass


class EmbeddingException(ApplicationException):
    """Raised when an embedding operation fails"""

    pass


class ModelNotFoundException(ApplicationException):
    """Raised when a specific model is not found in the database."""

    pass


class ModelCreationException(ApplicationException):
    """Raised when creating a new model fails."""

    pass


class ModelUpdateException(ApplicationException):
    """Raised when creating a new model fails."""

    pass


class ModelDeletionException(ApplicationException):
    """Raised when deleting a model fails."""

    pass


class ModelRetrievalException(ApplicationException):
    """Raised when retrieving a model fails."""

    pass


class ModelListingException(ApplicationException):
    """Raised when listing models fails (e.g., join of built-in + user models)."""

    pass


class ChatHistoryFetchException(ApplicationException):
    """Raised when fetching chat history fails."""

    pass


class ChatHistoryDeletionException(ApplicationException):
    """Raised when deleting chat history fails."""

    pass


class ChatMemoryBufferException(ApplicationException):
    """Raised when there is an issue with the chat memory buffer."""

    pass


class InvalidDataSourceConfigException(ApplicationException):
    """Raised when there is an issue with the chat memory buffer."""

    pass


class PromptNotFoundException(ApplicationException):
    """Raised when a specific model is not found in the database."""

    pass


class PromptCreationException(ApplicationException):
    """Raised when creating a new model fails."""

    pass


class PromptUpdateException(ApplicationException):
    """Raised when creating a new model fails."""

    pass


class PromptDeletionException(ApplicationException):
    """Raised when deleting a model fails."""

    pass


class PromptRetrievalException(ApplicationException):
    """Raised when retrieving a model fails."""

    pass


class PromptListingException(ApplicationException):
    """Raised when listing models fails (e.g., join of built-in + user models)."""

    pass


# ==================== AUTHENTICATION EXCEPTIONS ====================


class AuthenticationException(ApplicationException):
    """Base exception for authentication-related errors"""

    pass


class EmailAlreadyInUseException(AuthenticationException):
    """Raised when trying to register with an email that's already in use"""

    pass


class PhoneAlreadyInUseException(AuthenticationException):
    """Raised when trying to register with a phone number that's already in use"""

    pass


class InvalidCredentialsException(AuthenticationException):
    """Raised when login credentials are invalid"""

    pass


class UserNotVerifiedException(AuthenticationException):
    """Raised when user account is not verified (email not confirmed)"""

    pass


class UserAccountDisabledException(AuthenticationException):
    """Raised when user account is disabled"""

    pass


class InvalidTokenException(AuthenticationException):
    """Raised when JWT token is invalid or expired"""

    pass


class TokenExpiredException(AuthenticationException):
    """Raised when JWT token has expired"""

    pass


class RefreshTokenInvalidException(AuthenticationException):
    """Raised when refresh token is invalid or expired"""

    pass


class PasswordTooWeakException(AuthenticationException):
    """Raised when password doesn't meet security requirements"""

    pass


class InvalidEmailFormatException(AuthenticationException):
    """Raised when email format is invalid"""

    pass


class InvalidPhoneFormatException(AuthenticationException):
    """Raised when phone number format is invalid"""

    pass


class RegistrationFailedException(AuthenticationException):
    """Raised when user registration fails for any reason"""

    pass


class LoginFailedException(AuthenticationException):
    """Raised when user login fails for any reason"""

    pass


class LogoutFailedException(AuthenticationException):
    """Raised when user logout fails"""

    pass


class TokenRefreshFailedException(AuthenticationException):
    """Raised when token refresh fails"""

    pass


class EmailVerificationRequiredException(AuthenticationException):
    """Raised when email verification is required but not completed"""

    pass


class AccountLockedException(AuthenticationException):
    """Raised when account is locked due to too many failed attempts"""

    pass


class UnauthorizedAccessException(AuthenticationException):
    """Raised when user tries to access resource without proper authorization"""

    pass


class SessionExpiredException(AuthenticationException):
    """Raised when user session has expired"""

    pass


class UnknownAuthenticationException(AuthenticationException):
    """Raised when an unknown authentication error occurs"""

    pass
