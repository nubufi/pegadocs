from typing import Any, Dict, List
from loguru import logger

from app.application.exceptions import (
    PromptCreationException,
    PromptUpdateException,
    PromptDeletionException,
    PromptListingException,
    PromptNotFoundException,
    PromptRetrievalException,
)
from app.infra.config import settings
from app.infra.utils.supabase_utils import (
    add_item,
    delete_item,
    fetch_items,
    update_item,
)


class PromptService:
    """Service for system prompt operations related to database operations"""

    table_name = settings.PROMPT_TABLE_NAME

    def get_builtin_prompts(self) -> List[Dict[str, Any]]:
        logger.info("Fetching built-in prompts...")
        try:
            prompts = fetch_items(self.table_name, "user_id", None)
            logger.debug(f"Retrieved {len(prompts)} built-in prompts.")
            return prompts
        except Exception as e:
            logger.exception("Failed to fetch built-in prompts")
            raise PromptRetrievalException(f"Failed to get builtin prompts: {str(e)}")

    def get_user_defined_prompts(self, user_id: str) -> List[Dict[str, Any]]:
        logger.info(f"Fetching user-defined prompts for user_id={user_id}")
        try:
            prompts = fetch_items(self.table_name, "user_id", user_id)
            logger.debug(f"Retrieved {len(prompts)} user-defined prompts.")
            return prompts
        except Exception as e:
            logger.exception(f"Failed to retrieve user-defined prompts for {user_id}")
            raise PromptRetrievalException(
                f"Failed to get user-defined prompts: {str(e)}"
            )

    def list_prompts(self, user_id: str) -> List[Dict[str, Any]]:
        logger.info(f"Listing all prompts for user_id={user_id}")
        try:
            default_prompts = self.get_builtin_prompts()
            user_prompts = self.get_user_defined_prompts(user_id)
            total = len(default_prompts) + len(user_prompts)
            logger.debug(f"Total prompts returned: {total}")
            return default_prompts + user_prompts
        except Exception as e:
            logger.exception(f"Failed to list prompts for {user_id}")
            raise PromptListingException(f"Failed to list prompts: {str(e)}")

    def create_prompt(
        self,
        user_id: str,
        prompt_name: str,
        prompt_text: str,
    ) -> str:
        logger.info(f"Updating prompt '{prompt_name}' for user_id={user_id}")
        try:
            response = add_item(
                self.table_name,
                {
                    "user_id": user_id,
                    "name": prompt_name,
                    "prompt": prompt_text,
                },
            )
            prompt_id = response.data[0]["id"] if response.data else ""
            logger.debug(f"Prompt updated with ID: {prompt_id}")
            return prompt_id
        except Exception as e:
            logger.exception(f"Failed to update prompt '{prompt_name}' for {user_id}")
            raise PromptCreationException(f"Failed to generate prompt: {str(e)}")

    def update_prompt(
        self,
        user_id: str,
        prompt_id: str,
        prompt_name: str,
        prompt_text: str,
    ) -> str:
        logger.info(f"Update prompt '{prompt_name}' for user_id={user_id}")
        try:
            response = update_item(
                self.table_name,
                "id",
                prompt_id,
                {
                    "name": prompt_name,
                    "prompt": prompt_text,
                },
                user_id,
            )
            prompt_id = response.data[0]["id"] if response.data else ""
            logger.debug(f"Prompt created with ID: {prompt_id}")
            return prompt_id
        except Exception as e:
            logger.exception(f"Failed to create prompt '{prompt_name}' for {user_id}")
            raise PromptUpdateException(f"Failed to update prompt: {str(e)}")

    def delete_prompt(self, prompt_id: str, user_id: str) -> None:
        logger.info(
            f"Attempting to delete prompt with ID={prompt_id} for user_id={user_id}"
        )
        try:
            response = delete_item(self.table_name, "id", prompt_id, user_id)
        except Exception as e:
            logger.exception(f"Failed to delete prompt {prompt_id}")
            raise PromptDeletionException(f"Failed to delete prompt: {str(e)}")

        if not response.data:
            logger.warning(f"Prompt {prompt_id} not found for user_id={user_id}")
            raise PromptNotFoundException(f"prompt {prompt_id} not found.")
        logger.debug(f"Prompt {prompt_id} deleted successfully.")

    def get_prompt(self, prompt_id: str) -> dict:
        logger.info(f"Fetching prompt with ID={prompt_id}")
        try:
            logger.info(f"Fetching prompt {prompt_id} from table {self.table_name}")
            prompt = fetch_items(self.table_name, "id", prompt_id)
            if not prompt:
                logger.warning(f"Prompt {prompt_id} not found.")
                raise PromptNotFoundException(f"Prompt {prompt_id} not found.")
            logger.debug(f"Prompt {prompt_id} retrieved successfully.")
            return prompt[0]
        except Exception as e:
            logger.exception(f"Failed to retrieve prompt {prompt_id}")
            raise PromptNotFoundException(f"Failed to get prompt: {str(e)}")
