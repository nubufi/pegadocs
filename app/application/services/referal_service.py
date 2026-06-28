from typing import Optional
from app.infra.config import settings
from app.infra.utils.supabase_utils import add_item, fetch_items, supabase


class ReferalService:
    refenrence_codes_table = settings.REFERENCE_CODES_TABLE_NAME

    @staticmethod
    def _generate_reference_code(user_id: str) -> str:
        """
        Generate a reference code based on the user ID.

        Args:
            user_id (str): The ID of the user.
        Returns:
            str: The generated reference code.
        """
        return f"REF-{user_id[:8].upper()}"

    def add_reference_code(self, user_id: str):
        """
        Add a reference code to the reference codes table.

        Args:
            user_id (str): The ID of the user.
        """
        code = self._generate_reference_code(user_id)
        add_item(
            self.refenrence_codes_table,
            {
                "referer_user_id": user_id,
                "reference_code": code,
            },
        )

    def get_reference_code(self, user_id: str):
        """
        Retrieve the reference code for a given user.
        Args:
            user_id (str): The ID of the user.
        Returns:
            reference_code (str): The reference code of the user.
        """
        records = fetch_items(self.refenrence_codes_table, "referer_user_id", user_id)
        if records:
            return records[0].get("reference_code")
        return None

    def get_registration_bonus(self, reference_code: str):
        """
        Retrieve the referal bonuses for a given reference code.
        Args:
            reference_code (str): The reference code of the user.
        Returns:
            bonuses (float): The referal bonuses of the user.
        """
        records = fetch_items(
            self.refenrence_codes_table, "reference_code", reference_code
        )
        if records:
            return records[0].get("registration_bonus", 0.0)
        return 0.0

    def get_referer_user_id(self, reference_code: str):
        """
        Retrieve the target user ID for a given reference code.
        Args:
            reference_code (str): The reference code of the user.
        Returns:
            referer_user_id (str): The target user ID of the reference code.
        """
        records = fetch_items(
            self.refenrence_codes_table, "reference_code", reference_code
        )
        if records:
            return records[0].get("referer_user_id")
        return None

    def get_reference_code(self, user_id: str) -> Optional[str]:
        """
        Retrieve the reference code for a given user.
        Args:
            user_id (str): The ID of the user.
        Returns:
            reference_code (str): The reference code of the user.
        """
        user_metadata = supabase.auth.admin.get_user_by_id(user_id).user.user_metadata
        if user_metadata:
            return user_metadata.get("reference_code")
