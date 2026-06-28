from fastapi import APIRouter
from fastapi.responses import JSONResponse

health_router = APIRouter()


@health_router.get(
    "/health",
    summary="Health check endpoint",
    tags=["health"],
)
def health_check():
    status = {"status": "ok"}
    http_status = 200

    return JSONResponse(content=status, status_code=http_status)
