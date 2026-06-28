from typing import Optional

from app.application.services.referal_service import ReferalService
from app.presentation.schemas.reference_schemas import ReferenceCodeResponse


class ReferenceController:
    """Controller for reference code operations"""

    def __init__(self, referral_service: ReferalService):
        self.referral_service = referral_service

    def get_reference_code(self, user_id: str) -> ReferenceCodeResponse:
        """
        Handle reference code retrieval request

        Args:
            user_id (str): The ID of the authenticated user
        Returns:
            ReferenceCodeResponse: The response containing the reference code
        """
        reference_code = self.referral_service.get_reference_code(user_id)

        return ReferenceCodeResponse(
            reference_code=reference_code,
            message=(
                "Reference code retrieved successfully"
                if reference_code
                else "No reference code found"
            ),
        )
