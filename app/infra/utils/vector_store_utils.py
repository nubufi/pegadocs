from app.application.protocols.vector_store_protocol import VectorStoreProtocol
from app.application.services.database_service import DatabaseService
from app.infra.factories.vector_store import VectorStoreFactory


def get_vector_store(collection_id: str, user_id: str) -> VectorStoreProtocol:
    """
    Returns a vector store instance for the given collection name.

    Args:
        collection_id (str): The name of the collection to use for the vector store.
        user_id (str): The ID of the user who owns the collection.

    Returns:
        VectorStoreProtocol: An instance of the PostgresVectorStore with the specified collection name.
    """
    database_service = DatabaseService()
    vector_store = VectorStoreFactory.get_vector_store(
        collection_id, user_id, database_service
    )

    return vector_store
