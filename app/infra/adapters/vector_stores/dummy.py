from app.application.protocols.vector_store_protocol import VectorStoreProtocol


class DummyVS(VectorStoreProtocol):
    def __init__(self):
        self.collection_id = ""

    def delete_collection(self) -> None:
        """
        Deletes a collection from the PostgreSQL database.

        Args:
            delete_data_sources (bool): Whether to delete associated data sources. Defaults to True.
        """

        return None

    def get_vector_store(self) -> None:
        """
        Returns None as this is a dummy vector store.
        """
        return None
