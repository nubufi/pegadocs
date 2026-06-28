from app.infra.config import settings
from app.infra.utils.supabase_utils import fetch_items

COLLECTIONS_TABLE = settings.COLLECTIONS_TABLE_NAME
MODELS_TABLE = settings.MODELS_TABLE_NAME


def get_embedding_model_id_by_collection_id(
    collection_id: str,
    collections_table_name: str = COLLECTIONS_TABLE,
) -> str:
    """
    Retrieves the embedding model ID for a specific collection.

    Args:
        collection_id (str): The ID of the collection.
        collections_table_name (str): The name of the collections table. Defaults to COLLECTIONS_TABLE.

    Returns:
        str: The embedding model ID for the specified collection.
    """
    collection = fetch_items(collections_table_name, "id", collection_id)
    if not collection:
        raise ValueError(f"Collection with ID {collection_id} not found.")

    return collection[0]["embedding_model_id"]


def get_embedding_dim_by_collection_id(
    collection_id: str,
    collections_table_name: str = COLLECTIONS_TABLE,
    models_table_name: str = MODELS_TABLE,
) -> int:
    """
    Retrieves the embedding dimension for a specific collection.

    Args:
        collection_id (str): The ID of the collection.
        collections_table_name (str): The name of the collections table. Defaults to COLLECTIONS_TABLE.
        models_table_name (str): The name of the models table. Defaults to MODELS_TABLE.

    Returns:
        int: The embedding dimension for the specified collection.
    """
    collection = fetch_items(collections_table_name, "id", collection_id)
    if not collection:
        raise ValueError(f"Collection with ID {collection_id} not found.")

    embedding_model_id = collection[0]["embedding_model_id"]

    model = fetch_items(models_table_name, "id", embedding_model_id)

    if not model:
        raise ValueError(f"Model with ID {embedding_model_id} not found.")

    embedding_dim = model[0].get("dimensions")

    if embedding_dim is None:
        raise ValueError(
            f"Embedding dimension not found for model with ID {embedding_model_id}."
        )

    return int(embedding_dim)
