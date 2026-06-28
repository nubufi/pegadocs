import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore

from app.application.protocols.vector_store_protocol import VectorStoreProtocol


class ChromaVS(VectorStoreProtocol):
    def __init__(self, collection_id: str, config: dict, embded_dim: int = 1536):
        """
        Initialize the ChromaVectorStore with the collection name.

        Args:
            collection_id (str): The name of the collection to use in the vector store.
            embded_dim (int): The dimension of the embeddings. Defaults to 1536.
            config (dict): Configuration parameters for the vector store. It should inclued the following keys:
                - host: The host of the PostgreSQL database.
                - port: The port of the PostgreSQL database.

        """
        self.collection_id = collection_id
        self.config = config
        self.embedded_dim = embded_dim
        self.remote_db = chromadb.HttpClient(
            host=self.config["host"],
            port=self.config["port"],
        )

    def delete_collection(self) -> None:
        """
        Deletes a collection from the chroma db database.
        """

        self.remote_db.delete_collection(self.collection_id)

    def get_vector_store(self) -> ChromaVectorStore:
        """
        Get the vector store from Postgres.

        Returns:
            PGVectorStore: The vector store instance configured with the connection parameters.
        """
        collection = self.remote_db.get_or_create_collection(self.collection_id)

        return ChromaVectorStore(chroma_collection=collection)
