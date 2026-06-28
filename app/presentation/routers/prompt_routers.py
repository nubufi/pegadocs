from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.application.services.prompt_service import PromptService
from app.infra.auth import get_user
from app.infra.utils.fastapi_utils import gen_error_response
from app.presentation.controllers.prompt_controller import PromptController
from app.presentation.schemas.prompt_schemas import (
    CreatePromptRequest,
    CreatePromptResponse,
    ListPromptsResponse,
    UpdatePromptRequest,
    UpdatePromptResponse,
)

prompt_router = APIRouter()


@prompt_router.post(
    "/create-prompt",
    summary="Create a prompt for a user",
    response_model=CreatePromptResponse,
    tags=["prompts"],
)
def create_prompt(input: CreatePromptRequest, user_id=Depends(get_user)):
    try:
        prompt_service = PromptService()
        prompt_controller = PromptController(prompt_service)
        result = prompt_controller.create_prompt(input, user_id=user_id)
        return JSONResponse(status_code=200, content=result.model_dump())
    except Exception as e:
        return gen_error_response(e)


@prompt_router.get(
    "/list-prompts",
    summary="List all prompts available for a user",
    response_model=list[ListPromptsResponse],
    tags=["prompts"],
)
def list_prompts(user_id=Depends(get_user)):
    try:
        prompt_service = PromptService()
        prompt_controller = PromptController(prompt_service)
        result = prompt_controller.list_prompts(user_id=user_id)
        return JSONResponse(
            status_code=200, content=[item.model_dump() for item in result]
        )
    except Exception as e:
        return gen_error_response(e)


@prompt_router.delete(
    "/delete-prompt/{prompt_id}",
    summary="Delete user defined model",
    tags=["prompts"],
)
def delete_prompt(prompt_id: str, user_id=Depends(get_user)):
    try:
        prompt_service = PromptService()
        prompt_controller = PromptController(prompt_service)
        prompt_controller.delete_prompt(prompt_id=prompt_id, user_id=user_id)
        return JSONResponse(status_code=204, content=None)
    except Exception as e:
        return gen_error_response(e)


@prompt_router.post(
    "/update-prompt",
    summary="Update prompt for a user",
    response_model=UpdatePromptResponse,
    tags=["prompts"],
)
def update_prompt(input: UpdatePromptRequest, user_id=Depends(get_user)):
    try:
        prompt_service = PromptService()
        prompt_controller = PromptController(prompt_service)
        result = prompt_controller.update_prompt(input, user_id=user_id)
        return JSONResponse(status_code=200, content=result.model_dump())
    except Exception as e:
        return gen_error_response(e)
