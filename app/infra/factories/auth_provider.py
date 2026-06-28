from app.application.protocols.auth_provider import AuthProviderProtocol
from app.infra.config import settings


class AuthProviderFactory:
    @staticmethod
    def get_provider() -> AuthProviderProtocol:
        provider = settings.AUTH_PROVIDER.lower()
        if provider == "supabase":
            from app.infra.adapters.auth.supabase_auth_provider import SupabaseAuthProvider

            return SupabaseAuthProvider()
        elif provider == "local":
            from app.infra.adapters.auth.local_auth_provider import LocalAuthProvider

            return LocalAuthProvider()
        else:
            raise ValueError(f"Unknown AUTH_PROVIDER: {settings.AUTH_PROVIDER}. Must be 'supabase' or 'local'.")