from app.application.protocols.vector_store_protocol import VectorStoreProtocol
from app.application.services.database_service import DatabaseService
from app.infra.config import settings
from app.infra.utils.collection_utils import get_embedding_dim_by_collection_id
from app.infra.utils.encrypt_utils import decrypt_dict
from app.infra.utils.supabase_utils import fetch_items
from app.infra.adapters.vector_stores.dummy import DummyVS
from app.infra.adapters.vector_stores.pinecone import PineconeVS
from app.infra.adapters.vector_stores.chroma import ChromaVS
from app.infra.adapters.vector_stores.postgres import PostgresVS
from app.infra.adapters.vector_stores.s3 import S3VS


class VectorStoreFactory:
    """
    Factory class for creating vector store instances.
    """

    @staticmethod
    def get_vector_store(
        collection_id: str | None, user_id: str, database_service: DatabaseService
    ) -> VectorStoreProtocol:
        """
        Creates a vector store instance based on the collection_id.

        Args:
            collection_id (str): The name of the collection to use in the vector store.

        Returns:
            VectorStoreProtocol: An instance of PostgresVectorStore or AWSS3VectorStore based on the collection_id.
        """

        if not collection_id:
            return DummyVS()

        resp = fetch_items(settings.COLLECTIONS_TABLE_NAME, "id", collection_id)
        if not resp:
            raise ValueError(f"Collection with ID {collection_id} does not exist.")
        db_id = resp[0].get("database_id")
        if not db_id:
            raise ValueError(
                f"Collection with ID {collection_id} does not have a database ID."
            )
        database_index = database_service.get_database_index(db_id, user_id)
        if not database_index:
            raise ValueError(
                f"Database with ID {db_id} does not exist for user {user_id}."
            )

        database_config = decrypt_dict(database_index.get("config", {}))
        database_type = database_index.get("type", "")

        embed_dim = get_embedding_dim_by_collection_id(collection_id)
        if database_type == "postgres":
            return PostgresVS(collection_id, database_config, embed_dim)
        elif database_type == "s3":
            return S3VS(collection_id, database_config, embed_dim)
        elif database_type == "chromadb":
            return ChromaVS(collection_id, database_config, embed_dim)
        elif database_type == "pinecone":
            return PineconeVS(collection_id, database_config, embed_dim)
        else:
            raise ValueError(
                f"Unsupported database type: {database_type}. Only 'postgres' is supported."
            )
