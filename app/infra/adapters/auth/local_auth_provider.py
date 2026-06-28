import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import bcrypt
import jwt
from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.application.exceptions import (
    ApiKeyGenerationException,
    ApiKeyListException,
    ApiKeyRevokeException,
    EmailAlreadyInUseException,
    InvalidCredentialsException,
    InvalidTokenException,
    TokenRefreshFailedException,
)
from app.infra.adapters.auth.models import (
    LocalApiKey,
    LocalPasswordResetToken,
    LocalRefreshToken,
    LocalUser,
    get_session_local,
)
from app.infra.config import settings


def normalize_email(email: str) -> str:
    return email.strip().lower()


def _get_jwt_secret() -> str:
    return settings.LOCAL_AUTH_JWT_SECRET or settings.FERNET_SECRET_KEY


class LocalAuthProvider:
    def __init__(self):
        pass

    def _get_session(self) -> Session:
        return get_session_local()()

    def login(self, email: str, password: str) -> Tuple[str, str, str, int, Optional[str]]:
        email = normalize_email(email)
        logger.info(f"Attempting login for email={email}")
        with self._get_session() as session:
            user = session.execute(select(LocalUser).where(LocalUser.email == email)).scalar_one_or_none()
            if not user:
                raise InvalidCredentialsException("Invalid email or password")
            if not LocalUser.verify_password(password, user.password_hash):
                raise InvalidCredentialsException("Invalid email or password")

            access_token = self._create_access_token(user.id, user.email)
            expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

            refresh_token_str = str(uuid.uuid4())
            refresh_token_hash = hashlib.sha256(refresh_token_str.encode()).hexdigest()
            refresh_expires = datetime.now(timezone.utc) + timedelta(days=30)
            rt = LocalRefreshToken(user_id=user.id, token_hash=refresh_token_hash, expires_at=refresh_expires)
            session.add(rt)
            session.commit()

            logger.info(f"Login successful for user_id={user.id}")
            return user.id, access_token, refresh_token_str, expires_in, user.name

    def register(self, email: str, password: str, name: str, phone: str,
                 company: Optional[str] = None) -> Tuple[str, str]:
        email = normalize_email(email)
        logger.info(f"Attempting registration for email={email}")
        with self._get_session() as session:
            existing = session.execute(select(LocalUser).where(LocalUser.email == email)).scalar_one_or_none()
            if existing:
                raise EmailAlreadyInUseException("Email address is already in use")

            user = LocalUser(
                email=email,
                password_hash=LocalUser.hash_password(password),
                name=name,
                phone=phone,
                company=company,
                email_verified=True,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            logger.info(f"Registration successful for user_id={user.id}")
            return user.id, "Registration successful. You are now logged in."

    def refresh_token(self, refresh_token: str) -> Tuple[str, str, int]:
        logger.info("Attempting token refresh")
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        with self._get_session() as session:
            rt = session.execute(
                select(LocalRefreshToken).where(LocalRefreshToken.token_hash == token_hash)
            ).scalar_one_or_none()
            if not rt or rt.expires_at < datetime.now(timezone.utc):
                raise TokenRefreshFailedException("Invalid or expired refresh token")

            session.delete(rt)

            user = session.execute(select(LocalUser).where(LocalUser.id == rt.user_id)).scalar_one()
            access_token = self._create_access_token(user.id, user.email)
            expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

            new_refresh_str = str(uuid.uuid4())
            new_refresh_hash = hashlib.sha256(new_refresh_str.encode()).hexdigest()
            new_refresh_expires = datetime.now(timezone.utc) + timedelta(days=30)
            new_rt = LocalRefreshToken(user_id=user.id, token_hash=new_refresh_hash, expires_at=new_refresh_expires)
            session.add(new_rt)
            session.commit()

            logger.info("Token refresh successful")
            return access_token, new_refresh_str, expires_in

    def get_user_details(self, user_id: str) -> Tuple[str, Optional[str]]:
        logger.info(f"Fetching details for user_id={user_id}")
        with self._get_session() as session:
            user = session.execute(select(LocalUser).where(LocalUser.id == user_id)).scalar_one_or_none()
            if not user:
                raise Exception("User not found")
            return user.email, user.name

    def update_user_profile(self, user_id: str, name: Optional[str] = None,
                            phone: Optional[str] = None, company: Optional[str] = None) -> Tuple[str, str, str, str, Optional[str]]:
        logger.info(f"Attempting to update profile for user_id={user_id}")
        with self._get_session() as session:
            user = session.execute(select(LocalUser).where(LocalUser.id == user_id)).scalar_one_or_none()
            if not user:
                raise Exception("User not found")
            if name is not None:
                user.name = name
            if phone is not None:
                user.phone = phone
            if company is not None:
                user.company = company
            session.commit()
            session.refresh(user)
            logger.info(f"Profile updated successfully for user_id={user_id}")
            return user.id, user.email, user.name or "", user.phone or "", user.company

    def forgot_password(self, email: str) -> str:
        email = normalize_email(email)
        logger.info(f"Attempting to create password reset token for {email}")
        with self._get_session() as session:
            user = session.execute(select(LocalUser).where(LocalUser.email == email)).scalar_one_or_none()
            if not user:
                return "If an account with that email exists, a password reset link has been sent."
            reset_token = str(uuid.uuid4())
            expires = datetime.now(timezone.utc) + timedelta(hours=1)
            prt = LocalPasswordResetToken(user_id=user.id, token=reset_token, expires_at=expires)
            session.add(prt)
            session.commit()
            logger.info(f"Reset token: {reset_token}")
            return "If an account with that email exists, a password reset link has been sent."

    def reset_password(self, access_token: str, new_password: str) -> str:
        logger.info("Attempting to reset password")
        with self._get_session() as session:
            prt = session.execute(
                select(LocalPasswordResetToken).where(
                    LocalPasswordResetToken.token == access_token,
                    ~LocalPasswordResetToken.used,
                )
            ).scalar_one_or_none()
            if not prt or prt.expires_at < datetime.now(timezone.utc):
                raise InvalidTokenException("Invalid or expired token")
            user = session.execute(select(LocalUser).where(LocalUser.id == prt.user_id)).scalar_one_or_none()
            if not user:
                raise InvalidTokenException("Invalid or expired token")
            user.password_hash = LocalUser.hash_password(new_password)
            prt.used = True
            session.commit()
            logger.info("Password reset successfully")
            return "Password reset successfully. You can now log in with your new password."

    def resend_confirmation_email(self, email: str) -> str:
        logger.info(f"Resend confirmation email no-op for local mode: {email}")
        return "Confirmation email resent. Please check your inbox."

    def generate_api_key(self, user_id: str, expires_in_days: int, name: str) -> Tuple[str, str]:
        logger.info(f"Generating API key for user_id={user_id}, expires_in_days={expires_in_days}")
        try:
            api_key = f"sk_{uuid.uuid4().hex}"
            hashed = bcrypt.hashpw(api_key.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            key_id = str(uuid.uuid4())
            with self._get_session() as session:
                user = session.execute(select(LocalUser).where(LocalUser.id == user_id)).scalar_one_or_none()
                if not user:
                    raise ApiKeyGenerationException(f"User not found: {user_id}")
                expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)
                local_key = LocalApiKey(
                    key_id=key_id,
                    user_id=user_id,
                    api_key_hash=hashed,
                    name=name,
                    expires_at=expires_at,
                )
                session.add(local_key)
                session.commit()
            logger.debug(f"API key generated successfully with key_id={key_id}")
            return api_key, key_id
        except Exception as e:
            if isinstance(e, ApiKeyGenerationException):
                raise
            logger.error(f"Error generating API key for user_id={user_id}: {e}")
            raise ApiKeyGenerationException(f"Failed to generate API key: {str(e)}")

    def revoke_api_key(self, key_id: str) -> None:
        logger.info(f"Revoking API key with key_id={key_id}")
        try:
            with self._get_session() as session:
                local_key = session.execute(
                    select(LocalApiKey).where(LocalApiKey.key_id == key_id)
                ).scalar_one_or_none()
                if local_key:
                    session.delete(local_key)
                    session.commit()
            logger.debug(f"API key with key_id={key_id} successfully revoked")
        except Exception as e:
            logger.error(f"Error revoking API key with key_id={key_id}: {e}")
            raise ApiKeyRevokeException(f"Failed to revoke API key: {str(e)}")

    def list_api_keys(self, user_id: str) -> List[Dict[str, Any]]:
        logger.info(f"Listing API keys for user_id={user_id}")
        try:
            with self._get_session() as session:
                keys = session.execute(
                    select(LocalApiKey).where(LocalApiKey.user_id == user_id)
                ).scalars().all()
                return [
                    {
                        "key_id": k.key_id,
                        "expires_at": k.expires_at.isoformat(),
                        "created_at": k.created_at.isoformat(),
                        "name": k.name or "",
                    }
                    for k in keys
                ]
        except Exception as e:
            logger.error(f"Error listing API keys for user_id={user_id}: {e}")
            raise ApiKeyListException(f"Failed to list API keys: {str(e)}")

    def get_user_from_jwt(self, token: str) -> Optional[Any]:
        try:
            payload = jwt.decode(token, _get_jwt_secret(), algorithms=["HS256"])
            user_id = payload.get("sub")
            if user_id:
                from collections import namedtuple
                UserStub = namedtuple("UserStub", ["id"])
                return UserStub(id=user_id)
        except Exception:
            pass
        return None

    def get_user_from_api_key(self, api_key: str) -> Optional[str]:
        try:
            with self._get_session() as session:
                keys = session.execute(select(LocalApiKey)).scalars().all()
                for k in keys:
                    try:
                        if bcrypt.checkpw(api_key.encode("utf-8"), k.api_key_hash.encode("utf-8")):
                            if k.expires_at > datetime.now(timezone.utc):
                                return k.user_id
                    except Exception:
                        continue
        except Exception:
            pass
        return None

    def _create_access_token(self, user_id: str, email: str) -> str:
        expires = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": user_id,
            "email": email,
            "exp": expires,
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, _get_jwt_secret(), algorithm="HS256")