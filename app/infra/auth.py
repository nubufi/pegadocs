from typing import Optional, Any

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

_supabase = None


def _get_supabase() -> Client:
    global _supabase
    if _supabase is None:
        _supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    return _supabase

API_KEYS_TABLE_NAME = settings.API_KEYS_TABLE_NAME


def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def hash_api_key(api_key: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(api_key.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_api_key(api_key: str, hashed_key: str) -> bool:
    try:
        return bcrypt.checkpw(api_key.encode("utf-8"), hashed_key.encode("utf-8"))
    except Exception:
        return False


def list_api_keys(user_id: str):
    query = (
        _get_supabase().table(API_KEYS_TABLE_NAME)
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
    _get_supabase().table(API_KEYS_TABLE_NAME).delete().eq("key_id", key_id).execute()


def create_api_key(user_id: str, expires_in_days: int = 30, name: str = ""):
    import uuid
    from datetime import datetime, timedelta, timezone

    api_key = f"sk_{uuid.uuid4().hex}"
    hashed_api_key = hash_api_key(api_key)
    expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

    response = (
        _get_supabase().table(API_KEYS_TABLE_NAME)
        .insert(
            {
                "user_id": user_id,
                "api_key": hashed_api_key,
                "expires_at": expires_at.isoformat(),
                "name": name,
            }
        )
        .execute()
    )
    key_id = response.data[0]["key_id"] if response.data else None

    return api_key, key_id


def get_user_from_api_key(api_key: str):
    from datetime import datetime, timezone

    response = (
        _get_supabase().table(API_KEYS_TABLE_NAME)
        .select("user_id, api_key, expires_at")
        .execute()
    )

    if not response.data:
        return None

    for key_data in response.data:
        hashed_key = key_data["api_key"]
        if verify_api_key(api_key, hashed_key):
            expires_at = datetime.fromisoformat(
                key_data["expires_at"].replace("Z", "+00:00")
            )
            if datetime.now(timezone.utc) < expires_at:
                return key_data["user_id"]
            else:
                _get_supabase().table(API_KEYS_TABLE_NAME).delete().eq(
                    "api_key", hashed_key
                ).execute()

    return None


def get_user_from_jwt(token: str) -> Optional[Any]:
    try:
        response = _get_supabase().auth.get_user(token)
        if response and response.user:
            return response.user
        return None
    except Exception:
        return None


def get_user(
    authorization: Optional[str] = Header(None),
    api_key: Optional[str] = Security(api_key_header),
) -> str:
    if settings.AUTH_PROVIDER.lower() == "local":
        from app.infra.factories.auth_provider import AuthProviderFactory

        provider = AuthProviderFactory.get_provider()
        if authorization and authorization.startswith("Bearer "):
            jwt_token = authorization[7:]
            user = provider.get_user_from_jwt(jwt_token)
            if user:
                return user.id
        if api_key:
            user_id = provider.get_user_from_api_key(api_key)
            if user_id:
                return user_id
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication credentials",
        )

    if authorization and authorization.startswith("Bearer "):
        jwt_token = authorization[7:]
        user = get_user_from_jwt(jwt_token)
        if user:
            return user.id

    if api_key:
        user_id = get_user_from_api_key(api_key)
        if user_id:
            return user_id

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid authentication credentials",
    )