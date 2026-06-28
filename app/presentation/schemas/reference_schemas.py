from typing import Optional

from pydantic import BaseModel


class ReferenceCodeResponse(BaseModel):
    """Reference code response schema"""

    reference_code: Optional[str] = None
    message: str = "Reference code retrieved successfully"


class ReferenceCodeErrorResponse(BaseModel):
    """Reference code error response schema"""

    error: dict = {
        "code": "REFERENCE_CODE_ERROR",
        "message": "Failed to retrieve reference code",
        "type": "ReferenceCodeException",
    }
