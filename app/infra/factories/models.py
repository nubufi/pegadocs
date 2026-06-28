from app.application.models import PricedModel
from app.application.services.model_service import ModelService
from app.infra.adapters.models.azure_openai import AzureOpenAICM, AzureOpenAIEM


class ModelFactory:
    def __init__(self, model_service: ModelService):
        """
        Initialize the ModelFactory with a ModelService instance.

        Args:
            model_service (ModelService): An instance of the ModelService to interact with models.
        """
        self.model_service = model_service

    def get_embedding_model(self, model_id: str) -> PricedModel:
        model = self.model_service.get_model(model_id)
        provider = model["provider"]
        if provider == "azure_openai":
            return PricedModel(
                AzureOpenAIEM(model["config"]).get_embed_model(),
                input_price_per_1k_tokens=model.get("input_price_per_1k_tokens", 0.0),
                output_price_per_1k_tokens=model.get("output_price_per_1k_tokens", 0.0),
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def get_llm_model(self, model_id: str) -> PricedModel:
        model = self.model_service.get_model(model_id)
        provider = model["provider"]
        if provider == "azure_openai":
            return PricedModel(
                AzureOpenAICM(model["config"]).get_llm_model(),
                input_price_per_1k_tokens=model.get("input_price_per_1k_tokens", 0.0),
                output_price_per_1k_tokens=model.get("output_price_per_1k_tokens", 0.0),
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
