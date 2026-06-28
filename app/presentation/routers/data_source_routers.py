from loguru import logger
from typing import List
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.application.services.data_source_service import DataSourceService
from app.infra.auth import get_user
from app.presentation.controllers.data_source_controller import DataSourceController
from app.presentation.schemas.data_source_schemas import (
    CreateDataSourceRequest,
    CreateDataSourceResponse,
    ListDataSources,
    ListDataSourcesRequest,
    SASUrlRequest,
    SASUrlResponse,
    UpdateDataSourceRequest,
    UpdateDataSourceResponse,
)
from app.infra.utils.fastapi_utils import gen_error_response

data_source_router = APIRouter()

data_source_service = DataSourceService()
data_source_controller = DataSourceController(data_source_service)


@data_source_router.delete(
    "/delete-data-source/{data_source_id}",
    summary="Delete a specific data source from the collection",
    tags=["data_source"],
)
def delete_data_source_(data_source_id: str, user_id=Depends(get_user)):
    try:
        result = data_source_controller.delete_data_source(data_source_id, user_id)

        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        logger.error(f"Error deleting data source: {str(e)}")
        return gen_error_response(e)


@data_source_router.post(
    "/add-data-source",
    summary="Add a new data source to the vector store",
    tags=["data_source"],
    response_model=CreateDataSourceResponse,
)
def add_data_source_(input: CreateDataSourceRequest, user_id=Depends(get_user)):
    try:
        result = data_source_controller.add_data_source(input, user_id)

        return JSONResponse(content=result.model_dump(), status_code=200)
    except Exception as e:
        logger.error(f"Error adding data source: {str(e)}")
        return gen_error_response(e)


@data_source_router.post(
    "/list-data-sources",
    summary="List all data sources in a collection",
    tags=["data_source"],
    response_model=List[ListDataSources],
)
def list_data_sources_(input: ListDataSourcesRequest):
    try:
        result = data_source_controller.list_data_sources(input)

        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        logger.error(f"Error listing data sources: {str(e)}")
        return gen_error_response(e)


@data_source_router.post(
    "/update-data-source",
    summary="Update an existing data source in the vector store",
    tags=["data_source"],
    response_model=UpdateDataSourceResponse,
)
def update_data_source_(input: UpdateDataSourceRequest, user_id=Depends(get_user)):
    try:
        result = data_source_controller.update_data_source(input, user_id)

        return JSONResponse(content=result.model_dump(), status_code=200)
    except Exception as e:
        logger.error(f"Error adding data source: {str(e)}")
        return gen_error_response(e)


@data_source_router.post(
    "/get-sas-url",
    summary="Generate SAS URL for uploading files to Azure Blob Storage",
    response_model=SASUrlResponse,
    tags=["data_source"],
)
def get_sas_url(input: SASUrlRequest):
    try:
        result = data_source_controller.generate_sas_urls(input)
        return JSONResponse(content=result, status_code=202)
    except Exception as e:
        logger.error(f"Error generating SAS URL: {str(e)}")
        return gen_error_response(e)
