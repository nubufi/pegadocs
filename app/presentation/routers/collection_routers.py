from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from loguru import logger

from app.application.services.chat_service import ChatService
from app.application.services.collection_service import CollectionService
from app.application.services.data_source_service import DataSourceService
from app.application.services.database_service import DatabaseService
from app.infra.auth import get_user
from app.infra.factories.vector_store import VectorStoreFactory
from app.infra.utils.fastapi_utils import gen_error_response
from app.presentation.controllers.collection_controller import CollectionController
from app.presentation.schemas.collection_schemas import (
    CreateCollectionRequest,
    CreateCollectionResponse,
    ListCollectionsResponse,
)

collection_router = APIRouter()


def get_collection_controller(user_id: str, collection_id: str | None = None):
    database_service = DatabaseService()
    data_source_service = DataSourceService()
    vector_store = VectorStoreFactory.get_vector_store(
        collection_id, user_id, database_service
    )
    chat_service = ChatService(vector_store=vector_store, chat_store=None)
    collection_service = CollectionService(
        vector_store, data_source_service, chat_service
    )
    return CollectionController(collection_service)


@collection_router.delete(
    "/delete-collection/{collection_id}",
    summary="Delete a collection from the vector store",
    tags=["collection"],
)
def delete_collection(collection_id: str, user_id: str = Depends(get_user)):
    try:
        collection_controller = get_collection_controller(
            user_id=user_id, collection_id=collection_id
        )
        result = collection_controller.delete_collection(user_id)

        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        logger.error(f"Error deleting collection: {str(e)}")
        return gen_error_response(e)


@collection_router.get(
    "/list-collections",
    summary="List all collections in the vector store",
    tags=["collection"],
    response_model=List[ListCollectionsResponse],
)
def list_collections_(user_id: str = Depends(get_user)):
    try:
        collection_controller = get_collection_controller(user_id=user_id)
        result = collection_controller.list_collections(user_id)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        logger.error(f"Error listing collections: {str(e)}")
        return gen_error_response(e)


@collection_router.post(
    "/add-collection",
    summary="Add a new collection to the vector store",
    tags=["collection"],
    response_model=CreateCollectionResponse,
)
def add_collection(
    input: CreateCollectionRequest,
    user_id: str = Depends(get_user),
):
    try:
        collection_controller = get_collection_controller(user_id=user_id)
        result = collection_controller.create_collection(input, user_id)

        return JSONResponse(content=result.model_dump(), status_code=200)
    except Exception as e:
        logger.error(f"Error adding collection: {str(e)}")
        return gen_error_response(e)
