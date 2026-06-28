from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone

from app.application.protocols.vector_store_protocol import VectorStoreProtocol


class PineconeVS(VectorStoreProtocol):
    def __init__(self, collection_id: str, config: dict, embded_dim: int = 1536):
        """
        Initialize the ChromaVectorStore with the collection name.

        Args:
            collection_id (str): The name of the collection to use in the vector store.
            embded_dim (int): The dimension of the embeddings. Defaults to 1536.
            config (dict): Configuration parameters for the vector store. It should inclued the following keys:
                - api_key: The API key for Pinecone.
                - host: The host of the Pinecone service. Defaults to "api.pinecone.io".

        """
        self.collection_id = collection_id
        self.config = config
        self.embedded_dim = embded_dim
        self.client = Pinecone(
            api_key=self.config["api_key"],
            host=self.config.get("host", "api.pinecone.io"),
        )

    def delete_collection(self) -> None:
        """
        Deletes a collection from the chroma db database.
        """
        self.client.delete_collection(self.collection_id)

    def get_vector_store(self) -> PineconeVectorStore:
        """
        Get the vector store from Postgres.

        Returns:
            PGVectorStore: The vector store instance configured with the connection parameters.
        """
        collection = self.client.Index(self.collection_id)

        return PineconeVectorStore(pinecone_index=collection)
