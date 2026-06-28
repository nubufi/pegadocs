import boto3
from llama_index.vector_stores.s3 import S3VectorStore
from loguru import logger

from app.application.protocols.vector_store_protocol import VectorStoreProtocol


class S3VS(VectorStoreProtocol):
    def __init__(self, collection_id: str, config: dict, embded_dim: int = 1536):
        """
        Initialize the PostgresVectorStore with the collection name.

        Args:
            collection_id (str): The name of the collection to use in the vector store.
            embded_dim (int): The dimension of the embeddings. Defaults to 1536.
            config (dict): Configuration parameters for the vector store. It should inclued the following keys:
                - aws_access_key_id: The AWS access key ID.
                - aws_secret_access_key: The AWS secret access key.
                - aws_session_token: The AWS secret access key.
                - region: The AWS region where the vector store is hosted.
                - bucket_name: The name of the S3 bucket where the vector store is stored.

        """
        self.collection_id = collection_id
        self.embedded_dim = embded_dim
        self.bucket_name = config["bucket_name"]
        self.aws_session = boto3.Session(
            aws_secret_access_key=config["aws_secret_access_key"],
            aws_access_key_id=config["aws_access_key_id"],
            aws_session_token=config.get("aws_session_token"),
            region_name=config["region"],
        )
        self.s3_client = self.aws_session.client(
            "s3vectors",
            aws_secret_access_key=config["aws_secret_access_key"],
            aws_access_key_id=config["aws_access_key_id"],
            aws_session_token=config.get("aws_session_token"),
            region_name=config["region"],
        )

    def _get_vector_keys(self, data_source_id: str) -> list[str]:
        """
        Get the vector keys for a specific data source.

        Args:
            data_source_id (str): The ID of the data source.

        Returns:
            list[str]: A list of vector keys associated with the data source.
        """
        query_args = {
            "vectorBucketName": self.bucket_name,
            "indexName": self.collection_id,
            "queryVector": {"float32": [0.1] * self.embedded_dim},
            "topK": 30,
            "filter": {"data_source_id": {"$eq": data_source_id}},
        }
        response = self.s3_client.query_vectors(**query_args)
        vectors = response.get("vectors", [])
        vector_keys = [vec["key"] for vec in vectors]
        return vector_keys

    def delete_data_source(self, data_source_id: str) -> None:
        """
        Deletes a specific data source from the collection in the PostgreSQL database.
        Args:
            data_source_id (str): The ID of the data source to delete.
        """
        while self._get_vector_keys(data_source_id):
            vector_keys = self._get_vector_keys(data_source_id)
            logger.info(
                f"Found {len(vector_keys)} vectors to delete for data_source_id='{data_source_id}'"
            )
            self.s3_client.delete_vectors(
                vectorBucketName=self.bucket_name,
                indexName=self.collection_id,
                keys=vector_keys,
            )
        logger.info(
            f"Deleted vectors from vector store for data_source_id='{data_source_id}'"
        )

    def delete_collection(self) -> None:
        """
        Deletes a collection from the PostgreSQL database.
        """
        vector_store = self.get_vector_store()
        vector_store.clear()

    def check_index_exists_in_s3(self):
        """
        Check if an index (object) exists in an S3 bucket.

        Returns:
            bool: True if the index exists, False otherwise
        """
        try:
            self.s3_client.get_index(
                vectorBucketName=self.bucket_name, indexName=self.collection_id
            )
            return True

        except Exception as e:
            if "NotFoundException" in str(e):
                return False
            else:
                raise e

    def get_vector_store(self) -> S3VectorStore:
        """
        Get the vector store from Postgres.

        Returns:
            S3VectorStore: The vector store instance configured with the connection parameters.
        """
        if self.check_index_exists_in_s3():
            return S3VectorStore(
                bucket_name_or_arn=self.bucket_name,
                index_name_or_arn=self.collection_id,
                distance_metric="cosine",
                data_type="float32",
                sync_session=self.aws_session,
            )
        else:
            return S3VectorStore.create_index_from_bucket(
                bucket_name_or_arn=self.bucket_name,
                index_name=self.collection_id,
                dimension=self.embedded_dim,
                distance_metric="cosine",
                data_type="float32",
                sync_session=self.aws_session,
            )
