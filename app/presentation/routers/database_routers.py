from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.application.services.database_service import DatabaseService
from app.infra.auth import get_user
from app.infra.utils.fastapi_utils import gen_error_response
from app.presentation.controllers.database_controller import DataBaseController
from app.presentation.schemas.database_schemas import (
    CreateDataBaseIndexRequest,
    CreateDataBaseIndexResponse,
    ListDataBaseIndexResponse,
    UpdateDataBaseIndexRequest,
    UpdateDataBaseIndexResponse,
)

database_router = APIRouter()


@database_router.post(
    "/create-database-index",
    summary="Create a database index for a user",
    response_model=CreateDataBaseIndexResponse,
    tags=["database"],
)
def create_database_index(input: CreateDataBaseIndexRequest, user_id=Depends(get_user)):
    try:
        database_service = DatabaseService()
        database_controller = DataBaseController(database_service)
        result = database_controller.create_database_index(input, user_id=user_id)
        return JSONResponse(status_code=200, content=result.model_dump())
    except Exception as e:
        return gen_error_response(e)


@database_router.get(
    "/list-database-indexes",
    summary="List all database indexes for a user",
    response_model=list[ListDataBaseIndexResponse],
    tags=["database"],
)
def list_database_indexes(user_id=Depends(get_user)):
    try:
        database_service = DatabaseService()
        database_controller = DataBaseController(database_service)
        result = database_controller.list_database_indexes(user_id=user_id)
        return JSONResponse(
            status_code=200, content=[item.model_dump() for item in result]
        )
    except Exception as e:
        return gen_error_response(e)


@database_router.delete(
    "/delete-database-index/{db_id}",
    summary="Delete a database index",
    tags=["database"],
)
def delete_database_index(db_id: str, user_id=Depends(get_user)):
    try:
        database_service = DatabaseService()
        database_controller = DataBaseController(database_service)
        database_controller.delete_database_index(db_id=db_id, user_id=user_id)
        return JSONResponse(status_code=204, content=None)
    except Exception as e:
        return gen_error_response(e)


@database_router.post(
    "/update-database-index",
    summary="Updates database index for a user",
    response_model=UpdateDataBaseIndexResponse,
    tags=["database"],
)
def update_database_index(input: UpdateDataBaseIndexRequest):
    try:
        database_service = DatabaseService()
        database_controller = DataBaseController(database_service)
        result = database_controller.update_database_index(input)
        return JSONResponse(status_code=200, content=result.model_dump())
    except Exception as e:
        return gen_error_response(e)
