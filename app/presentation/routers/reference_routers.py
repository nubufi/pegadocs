from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.application.services.referal_service import ReferalService
from app.infra.auth import get_user
from app.infra.utils.fastapi_utils import gen_error_response
from app.presentation.controllers.reference_controller import ReferenceController
from app.presentation.schemas.reference_schemas import (
    ReferenceCodeErrorResponse,
    ReferenceCodeResponse,
)

reference_router = APIRouter()


@reference_router.get(
    "/reference_code/",
    summary="Get reference code for authenticated user",
    response_model=ReferenceCodeResponse,
    responses={
        200: {
            "model": ReferenceCodeResponse,
            "description": "Reference code retrieved successfully",
        },
        401: {
            "model": ReferenceCodeErrorResponse,
            "description": "Authentication required",
        },
        500: {
            "model": ReferenceCodeErrorResponse,
            "description": "Internal server error",
        },
    },
    tags=["reference"],
)
def get_reference_code(user_id: str = Depends(get_user)):
    """
    Get reference code for the authenticated user.
    Returns the user's reference code if available.
    """
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    referral_service = ReferalService()
    reference_controller = ReferenceController(referral_service)

    try:
        result = reference_controller.get_reference_code(user_id)
        return JSONResponse(
            content={
                "reference_code": result.reference_code,
                "message": result.message,
            },
            status_code=200,
        )
    except Exception as e:
        return gen_error_response(e)
