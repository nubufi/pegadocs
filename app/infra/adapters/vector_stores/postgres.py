from contextlib import contextmanager
from typing import Any, Generator, Optional, Tuple
from llama_index.vector_stores.postgres import PGVectorStore
import psycopg2

from app.application.protocols.vector_store_protocol import VectorStoreProtocol


class PostgresVS(VectorStoreProtocol):
    def __init__(self, collection_id: str, config: dict, embded_dim: int = 1536):
        """
        Initialize the PostgresVectorStore with the collection name.

        Args:
            collection_id (str): The name of the collection to use in the vector store.
            embded_dim (int): The dimension of the embeddings. Defaults to 1536.
            config (dict): Configuration parameters for the vector store. It should inclued the following keys:
                - database: The name of the database.
                - host: The host of the PostgreSQL database.
                - password: The password for the PostgreSQL database.
                - port: The port of the PostgreSQL database.
                - user: The user for the PostgreSQL database.
                - schema: The schema to use in the PostgreSQL database.

        """
        self.collection_id = collection_id
        self.config = config
        self.embedded_dim = embded_dim

    @contextmanager
    def execute_query(
        self, query: str, params: Optional[Tuple[Any, ...]] = None
    ) -> Generator[Any, None, None]:
        """
        Context manager to execute a SQL query and yield the cursor.

        Args:
            query (str): SQL query string.
            params (Optional[Tuple[Any, ...]]): Parameters to pass with the query.

        Yields:
            psycopg2.extensions.cursor: The cursor after executing the query.
        """
        conn = psycopg2.connect(
            dbname=self.config.get("database"),
            user=self.config.get("user"),
            password=self.config.get("password"),
            host=self.config.get("host"),
            port=self.config.get("port"),
        )
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    yield cur
        finally:
            conn.close()

    def delete_collection(self) -> None:
        """
        Deletes a collection from the PostgreSQL database.
        """
        query = f"""
        DROP TABLE IF EXISTS "{self.collection_id}" CASCADE;
        """
        with self.execute_query(query) as _:
            pass

    def get_vector_store(self) -> PGVectorStore:
        """
        Get the vector store from Postgres.

        Returns:
            PGVectorStore: The vector store instance configured with the connection parameters.
        """
        return PGVectorStore.from_params(
            database=self.config.get("database"),
            host=self.config.get("host"),
            password=self.config.get("password"),
            port=str(self.config.get("port")),
            user=self.config.get("user"),
            table_name=self.collection_id,
            embed_dim=self.embedded_dim,
            schema_name=self.config.get("schema", "public"),
            create_engine_kwargs={"pool_pre_ping": True, "pool_recycle": 299},
            hnsw_kwargs={
                "hnsw_m": 16,
                "hnsw_ef_construction": 64,
                "hnsw_ef_search": 40,
                "hnsw_dist_method": "vector_cosine_ops",
            },
        )
