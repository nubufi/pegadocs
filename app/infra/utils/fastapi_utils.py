from fastapi import HTTPException
from fastapi.responses import JSONResponse


def gen_error_response(error: Exception, status_code=500) -> JSONResponse:
    """Return a JSON response with error details."""
    if isinstance(error, HTTPException):
        status_code = error.status_code
    return JSONResponse(
        content={
            "detail": str(error),
            "error_type": type(error).__name__,
        },
        status_code=status_code,
    )
