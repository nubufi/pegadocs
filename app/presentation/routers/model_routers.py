from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.application.services.model_service import ModelService
from app.infra.auth import get_user
from app.infra.utils.fastapi_utils import gen_error_response
from app.presentation.controllers.model_controller import ModelController
from app.presentation.schemas.model_schemas import (
    CreateModelRequest,
    CreateModelResponse,
    ListModelsResponse,
    UpdateModelRequest,
    UpdateModelResponse,
)

model_router = APIRouter()


@model_router.post(
    "/create-model",
    summary="Create a model for a user",
    response_model=CreateModelResponse,
    tags=["models"],
)
def create_model(input: CreateModelRequest, user_id=Depends(get_user)):
    try:
        model_service = ModelService()
        model_controller = ModelController(model_service)
        result = model_controller.create_model(input, user_id=user_id)
        return JSONResponse(status_code=200, content=result.model_dump())
    except Exception as e:
        return gen_error_response(e)


@model_router.get(
    "/list-models",
    summary="List all models available for a user",
    response_model=list[ListModelsResponse],
    tags=["models"],
)
def list_modeles(user_id=Depends(get_user)):
    try:
        model_service = ModelService()
        model_controller = ModelController(model_service)
        result = model_controller.list_models(user_id=user_id)
        return JSONResponse(
            status_code=200, content=[item.model_dump() for item in result]
        )
    except Exception as e:
        return gen_error_response(e)


@model_router.delete(
    "/delete-model/{db_id}",
    summary="Delete user defined model",
    tags=["models"],
)
def delete_model(db_id: str, user_id=Depends(get_user)):
    try:
        model_service = ModelService()
        model_controller = ModelController(model_service)
        model_controller.delete_model(db_id=db_id, user_id=user_id)
        return JSONResponse(status_code=204, content=None)
    except Exception as e:
        return gen_error_response(e)


@model_router.post(
    "/update-model",
    summary="Updates model for a user",
    response_model=UpdateModelResponse,
    tags=["models"],
)
def update_model(input: UpdateModelRequest, user_id=Depends(get_user)):
    try:
        model_service = ModelService()
        model_controller = ModelController(model_service)
        result = model_controller.update_model(input, user_id=user_id)
        return JSONResponse(status_code=200, content=result.model_dump())
    except Exception as e:
        return gen_error_response(e)
