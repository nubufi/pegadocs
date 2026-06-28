from app.application.protocols.storage_provider import StorageProviderProtocol
from app.infra.config import settings


class StorageProviderFactory:
    @staticmethod
    def get_provider() -> StorageProviderProtocol:
        provider = settings.AUTH_PROVIDER.lower()
        if provider == "supabase":
            from app.infra.adapters.storage.supabase_storage_provider import SupabaseStorageProvider

            return SupabaseStorageProvider()
        elif provider == "local":
            from app.infra.adapters.storage.sqlalchemy_storage_provider import SQLAlchemyStorageProvider

            return SQLAlchemyStorageProvider()
        else:
            raise ValueError(f"Unknown AUTH_PROVIDER: {settings.AUTH_PROVIDER}. Must be 'supabase' or 'local'.")