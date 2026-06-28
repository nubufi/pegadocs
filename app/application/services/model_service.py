from typing import Any, Dict, List, Literal
from loguru import logger


from app.application.exceptions import (
    ModelCreationException,
    ModelDeletionException,
    ModelListingException,
    ModelNotFoundException,
    ModelRetrievalException,
    ModelUpdateException,
)
from app.infra.config import settings
from app.infra.utils.encrypt_utils import decrypt_dict, encrypt_dict
from app.infra.utils.supabase_utils import (
    add_item,
    delete_item,
    fetch_items,
    update_item,
)


class ModelService:
    """Service for database operations related to database operations"""

    table_name = settings.MODELS_TABLE_NAME

    def get_builtin_models(self) -> List[Dict[str, Any]]:
        logger.info("Fetching built-in models...")
        try:
            models = fetch_items(self.table_name, "user_id", None)
            for model in models:
                if "config" in model:
                    model["config"] = {}
            logger.debug(f"Retrieved {len(models)} built-in models.")
            return models
        except Exception as e:
            logger.exception("Failed to fetch built-in models")
            raise ModelRetrievalException(f"Failed to get builtin models: {str(e)}")

    def get_user_defined_models(self, user_id: str) -> List[Dict[str, Any]]:
        logger.info(f"Fetching user-defined models for user_id={user_id}")
        try:
            models = fetch_items(self.table_name, "user_id", user_id)
            for model in models:
                if "config" in model:
                    model["config"] = decrypt_dict(model["config"])
            logger.debug(f"Retrieved {len(models)} user-defined models.")
            return models
        except Exception as e:
            logger.exception(f"Failed to retrieve user-defined models for {user_id}")
            raise ModelRetrievalException(
                f"Failed to get user-defined models: {str(e)}"
            )

    def list_models(self, user_id: str) -> List[Dict[str, Any]]:
        logger.info(f"Listing all models for user_id={user_id}")
        try:
            default_models = self.get_builtin_models()
            user_models = self.get_user_defined_models(user_id)
            total = len(default_models) + len(user_models)
            logger.debug(f"Total models returned: {total}")
            return default_models + user_models
        except Exception as e:
            logger.exception(f"Failed to list models for {user_id}")
            raise ModelListingException(f"Failed to list models: {str(e)}")

    def create_model(
        self,
        user_id: str,
        model_name: str,
        model_type: Literal["chat", "embedding"],
        dimensions: int | None,
        provider: str | None,
        config: Dict[str, Any],
    ) -> str:
        logger.info(f"Creating model '{model_name}' for user_id={user_id}")
        try:
            encrypted_config = encrypt_dict(config)
            response = add_item(
                self.table_name,
                {
                    "user_id": user_id,
                    "name": model_name,
                    "type": model_type,
                    "dimensions": dimensions,
                    "config": encrypted_config,
                    "provider": provider,
                },
            )
            model_id = response.data[0]["id"] if response.data else ""
            logger.debug(f"Model created with ID: {model_id}")
            return model_id
        except Exception as e:
            logger.exception(f"Failed to create model '{model_name}' for {user_id}")
            raise ModelCreationException(f"Failed to generate model: {str(e)}")

    def update_model(
        self,
        user_id: str,
        model_id: str,
        model_name: str,
        model_type: Literal["chat", "embedding"],
        dimensions: int | None,
        provider: str | None,
        config: Dict[str, Any],
    ) -> str:
        logger.info(f"Updating model '{model_name}' for model_id={model_id}")
        try:
            encrypted_config = encrypt_dict(config)
            update_item(
                self.table_name,
                "id",
                model_id,
                {
                    "name": model_name,
                    "type": model_type,
                    "dimensions": dimensions,
                    "config": encrypted_config,
                    "provider": provider,
                },
                user_id,
            )
            logger.debug(f"Model updated with ID: {model_id}")
            return model_id
        except Exception as e:
            logger.exception(f"Failed to create model '{model_name}' for {model_id}")
            raise ModelUpdateException(f"Failed to generate model: {str(e)}")

    def delete_model(self, model_id: str, user_id: str) -> None:
        logger.info(
            f"Attempting to delete model with ID={model_id} for user_id={user_id}"
        )
        try:
            response = delete_item(self.table_name, "id", model_id, user_id)
        except Exception as e:
            logger.exception(f"Failed to delete model {model_id}")
            raise ModelDeletionException(f"Failed to delete model: {str(e)}")

        if not response.data:
            logger.warning(f"Model {model_id} not found for user_id={user_id}")
            raise ModelNotFoundException(f"model {model_id} not found.")
        logger.debug(f"Model {model_id} deleted successfully.")

    def get_model(self, model_id: str) -> dict:
        logger.info(f"Fetching model with ID={model_id}")
        try:
            model = fetch_items(self.table_name, "id", model_id)[0]
            model["config"] = decrypt_dict(model["config"])
            logger.debug(f"Model {model_id} retrieved successfully.")
            return model
        except Exception as e:
            logger.exception(f"Failed to retrieve model {model_id}")
            raise ModelNotFoundException(f"Failed to get model: {str(e)}")
