from typing import Any, Dict, List, Optional, Protocol, Tuple, runtime_checkable


@runtime_checkable
class AuthProviderProtocol(Protocol):
    def login(self, email: str, password: str) -> Tuple[str, str, str, int, Optional[str]]:
        ...

    def register(self, email: str, password: str, name: str, phone: str,
                 company: Optional[str] = None) -> Tuple[str, str]:
        ...

    def refresh_token(self, refresh_token: str) -> Tuple[str, str, int]:
        ...

    def get_user_details(self, user_id: str) -> Tuple[str, Optional[str]]:
        ...

    def update_user_profile(self, user_id: str, name: Optional[str] = None,
                            phone: Optional[str] = None, company: Optional[str] = None) -> Tuple[str, str, str, str, Optional[str]]:
        ...

    def forgot_password(self, email: str) -> str:
        ...

    def reset_password(self, access_token: str, new_password: str) -> str:
        ...

    def resend_confirmation_email(self, email: str) -> str:
        ...

    def generate_api_key(self, user_id: str, expires_in_days: int, name: str) -> Tuple[str, str]:
        ...

    def revoke_api_key(self, key_id: str) -> None:
        ...

    def list_api_keys(self, user_id: str) -> List[Dict[str, Any]]:
        ...

    def get_user_from_jwt(self, token: str) -> Optional[Any]:
        ...

    def get_user_from_api_key(self, api_key: str) -> Optional[str]:
        ...