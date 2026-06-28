from typing import Protocol, Sequence, List

from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.schema import BaseNode
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters

from app.infra.config import settings
from app.infra.utils.supabase_utils import fetch_items


class VectorStoreProtocol(Protocol):
    collection_id: str

    def check_collection(self) -> bool:
        """
        Checks if a collection table exists and has data in it using SQLAlchemy SessionLocal.

        Returns:
            bool: True if the table exists and has data, False otherwise.
        """
        collection_items = fetch_items(
            settings.COLLECTIONS_TABLE_NAME, "id", self.collection_id
        )
        data_source_items = fetch_items(
            settings.DATA_SOURCES_TABLE_NAME, "collection_id", self.collection_id
        )

        if not collection_items or not data_source_items:
            return False

        return True

    def delete_collection(self) -> None:
        """
        Deletes a collection from the PostgreSQL database.

        """
        raise NotImplementedError(
            "This method should be implemented in the subclass to delete the collection."
        )

    def delete_data_source(self, data_source_id: str) -> None:
        """
        Deletes a specific data source from the collection in the PostgreSQL database.
        Args:
            data_source_id (str): The ID of the data source to delete.
        """
        filters: List[MetadataFilter] = [
            MetadataFilter(key="data_source_id", value=data_source_id)
        ]
        vector_store = self.get_vector_store()
        vector_store.delete_nodes(filters=MetadataFilters(filters=filters))

    def get_vector_store(self):
        """
        Get the vector store index from the collection.

        Returns:
            VectorStoreIndex: The index containing the vector store data.
        """
        raise NotImplementedError

    def create_index(
        self,
        nodes: Sequence[BaseNode],
        embedding_model: BaseEmbedding,
        callback_manager=None,
    ) -> VectorStoreIndex:
        """
        Create an index in the vector store from the provided nodes.

        Args:
            nodes (List[BaseNode]): The list of nodes to index.
            embedding_model (BaseEmbedding): The embedding model to use for the nodes.
        Returns:
            VectorStoreIndex: The index created from the nodes.
        """
        vector_store = self.get_vector_store()
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        return VectorStoreIndex(
            nodes,
            storage_context=storage_context,
            embed_model=embedding_model,
            callback_manager=callback_manager,
        )

    def get_index(
        self, embedding_model: BaseEmbedding, callback_manager=None
    ) -> VectorStoreIndex:
        """
        Get the vector store index from the Supabase vector store.

        Args:
            embedding_model (BaseEmbedding): The embedding model to use for the index.
            callback_manager (CallbackManager, optional): The callback manager for token counting.

        Returns:
            VectorStoreIndex: The index containing the vector store data.
        """
        vector_store = self.get_vector_store()
        return VectorStoreIndex.from_vector_store(
            vector_store, embed_model=embedding_model, callback_manager=callback_manager
        )
