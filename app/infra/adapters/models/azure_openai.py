from typing import Dict
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding


class AzureOpenAIEM:
    def __init__(self, config: Dict[str, str]):
        """
        Initialize the AzureOpenAIEM with the configuration string.

        Args:
            config (str): The configuration string for the Azure OpenAI embedding model.
            It should include the following keys:
                - model: The model name to use.
                - deployment_name: The deployment name for the model.
                - api_key: The API key for authentication.
                - azure_endpoint: The Azure endpoint URL.
                - api_version: The API version to use.
        """
        self.config = config

    def get_embed_model(self) -> AzureOpenAIEmbedding:
        """
        Get the Azure OpenAI embedding model instance based on the configuration.

        Returns:
            AzureOpenAIEmbedding: An instance of the Azure OpenAI embedding model.
        """
        return AzureOpenAIEmbedding(
            model=self.config["model"],
            deployment_name=self.config["deployment_name"],
            api_key=self.config["api_key"],
            azure_endpoint=self.config["azure_endpoint"],
            api_version=self.config["api_version"],
        )


class AzureOpenAICM:
    def __init__(
        self,
        config: Dict[str, str],
        input_price_per_1k_tokens: float = 0.0,
        output_price_per_1k_tokens: float = 0.0,
    ):
        """
        Initialize the AzureOpenAICM with the configuration string.

        Args:
            config (str): The configuration string for the Azure OpenAI model.
            It should include the following keys:
                - model: The model name to use.
                - deployment_name: The deployment name for the model.
                - api_key: The API key for authentication.
                - azure_endpoint: The Azure endpoint URL.
                - api_version: The API version to use.
        """
        self.config = config
        self.input_price_per_1k_tokens = input_price_per_1k_tokens
        self.output_price_per_1k_tokens = output_price_per_1k_tokens

    def get_llm_model(self) -> AzureOpenAI:
        """
        Get the Azure OpenAI model instance based on the configuration.

        Returns:
            AzureOpenAI: An instance of the Azure OpenAI model.
        """
        return AzureOpenAI(
            model=self.config["model"],
            deployment_name=self.config["deployment_name"],
            api_key=self.config["api_key"],
            azure_endpoint=self.config["azure_endpoint"],
            api_version=self.config["api_version"],
        )
