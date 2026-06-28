import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import bcrypt
from fastapi import Header, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from supabase import Client, create_client

from app.infra.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY = settings.SUPABASE_SERVICE_ROLE_KEY

from loguru import logger

logger.info(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
print(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
# Init client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

API_KEYS_TABLE_NAME = settings.API_KEYS_TABLE_NAME


def get_supabase_client() -> Client:
    """
    Returns the Supabase client instance.
    Returns:
        Client: The Supabase client.
    """
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key using bcrypt for secure storage.
    Args:
        api_key (str): The raw API key to hash.
    Returns:
        str: The hashed API key.
    """
    # Generate a salt and hash the API key
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(api_key.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """
    Verify an API key against its hashed version.
    Args:
        api_key (str): The raw API key to verify.
        hashed_key (str): The hashed API key to compare against.
    Returns:
        bool: True if the API key matches, False otherwise.
    """
    try:
        return bcrypt.checkpw(api_key.encode("utf-8"), hashed_key.encode("utf-8"))
    except Exception:
        return False


def list_api_keys(user_id: str):
    """
    Lists all API keys for a given user and optionally for a specific project.
    Args:
        user_id (str): The ID of the user.
    Returns:
        list: A list of API keys associated with the user and project.
    """
    query = (
        supabase.table(API_KEYS_TABLE_NAME)
        .select("key_id, expires_at, created_at", "name")
        .eq("user_id", user_id)
    )
    response = query.execute()
    if response.data:
        return [
            {
                "key_id": key["key_id"],
                "expires_at": key["expires_at"],
                "created_at": key["created_at"],
                "name": key.get("name", ""),
            }
            for key in response.data
        ]
    return []


def revoke_api_key(key_id: str):
    """
    Revokes the API key by deleting it from the database.
    Args:
        key_id (str): The ID of the API key to revoke.
    Returns:
        bool: True if the API key was successfully revoked, False otherwise.
    """
    supabase.table(API_KEYS_TABLE_NAME).delete().eq("key_id", key_id).execute()


def create_api_key(user_id: str, expires_in_days: int = 30, name: str = ""):
    """
    Creates a new API key for the given user and project.
    Args:
        user_id (str): The ID of the user.
        expires_in_days (int): The number of days until the API key expires. Default is 30 days.
    Returns:
        tuple: A tuple containing the raw API key and the key ID.
    """
    api_key = f"sk_{uuid.uuid4().hex}"
    hashed_api_key = hash_api_key(api_key)
    expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

    response = (
        supabase.table(API_KEYS_TABLE_NAME)
        .insert(
            {
                "user_id": user_id,
                "api_key": hashed_api_key,  # Store hashed version
                "expires_at": expires_at.isoformat(),
                "name": name,
            }
        )
        .execute()
    )
    key_id = response.data[0]["key_id"] if response.data else None

    return api_key, key_id  # Return raw key for user, but store hashed


def get_user_from_api_key(api_key: str):
    """
    Retrieves the user ID associated with the provided API key.
    Args:
        api_key (str): The API key to check.
    Returns:
        str: The user ID associated with the API key, or None if not found.
    """
    # Get all API keys for comparison (since we can't query by hashed value)
    response = (
        supabase.table(API_KEYS_TABLE_NAME)
        .select("user_id, api_key, expires_at")
        .execute()
    )

    if not response.data:
        return None

    # Check each hashed key against the provided API key
    for key_data in response.data:
        hashed_key = key_data["api_key"]
        if verify_api_key(api_key, hashed_key):
            # Check if key is not expired
            expires_at = datetime.fromisoformat(
                key_data["expires_at"].replace("Z", "+00:00")
            )
            if datetime.now(timezone.utc) < expires_at:
                return key_data["user_id"]
            else:
                # Key is expired, remove it
                supabase.table(API_KEYS_TABLE_NAME).delete().eq(
                    "api_key", hashed_key
                ).execute()

    return None


def get_user_from_jwt(token: str) -> Optional[Any]:
    """
    Retrieves the user ID from a JWT token using Supabase authentication.
    Args:
        token (str): The JWT token.
    Returns:
        Optional[str]: The user ID if the token is valid, None otherwise.
    """
    try:
        # Use the existing Supabase client and pass JWT token to get_user()
        response = supabase.auth.get_user(token)

        if response and response.user:
            return response.user
        return None
    except Exception:
        return None


def get_user(
    authorization: Optional[str] = Header(None),
    api_key: Optional[str] = Security(api_key_header),
) -> str:
    """
    Dual authentication dependency supporting both JWT and API key authentication.
    Priority: JWT first, then API key if JWT not present.

    Args:
        authorization (str, optional): Authorization header with Bearer token.
        api_key (str, optional): API key from X-API-Key header.

    Returns:
        str: The user ID from either authentication method.

    Raises:
        HTTPException: If neither authentication method is valid.
    """
    # Try JWT authentication first
    if authorization and authorization.startswith("Bearer "):
        jwt_token = authorization[7:]  # Remove "Bearer " prefix
        user = get_user_from_jwt(jwt_token)
        if user:
            return user.id

    # Fall back to API key authentication
    if api_key:
        user_id = get_user_from_api_key(api_key)
        if user_id:
            return user_id

    # If neither method provided valid authentication
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid authentication credentials",
    )
