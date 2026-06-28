"""
Token counter context manager for tracking token usage in vector store and chat operations.

This module provides a thread-safe context manager that can be used to track token usage
across different llama-index operations including vector store indexing and chat engine interactions.
"""

from contextlib import contextmanager
from typing import Dict, Iterable, Optional

import tiktoken
from llama_index.core.callbacks import CallbackManager, TokenCountingHandler
from loguru import logger

from app.application.models import PricedModel


class TokenCounter:
    """
    A thread-safe token counter that tracks token usage for both LLM and embedding operations.

    This class provides methods to track tokens used by different models and calculate costs
    based on pricing information.
    """

    def __init__(
        self,
        embedding_model: PricedModel,
        llm_model: PricedModel | None = None,
    ):
        """
        Initialize the token counter with LLM and embedding models and pricing information.

        Args:
            embedding_model: The embedding model to track tokens for
            llm_model: The LLM model to track tokens for
        """
        self.llm_model = llm_model
        self.embedding_model = embedding_model
        self.llm_input_price_per_1k = (
            llm_model.input_price_per_1k_tokens if llm_model else 0.0
        )
        self.llm_output_price_per_1k = (
            llm_model.output_price_per_1k_tokens if llm_model else 0.0
        )
        self.embedding_price_per_1k = embedding_model.input_price_per_1k_tokens

        # Create token counting handlers with appropriate tokenizers
        self.llm_token_counter = (
            TokenCountingHandler(tokenizer=self._get_llm_tokenizer())
            if llm_model
            else None
        )
        self.embedding_token_counter = TokenCountingHandler(
            tokenizer=self._get_embedding_tokenizer()
        )

        # Create callback manager with both counters
        self.callback_manager = CallbackManager(
            [self.llm_token_counter, self.embedding_token_counter]
            if self.llm_token_counter
            else [self.embedding_token_counter]
        )

    def _get_llm_tokenizer(self):
        """Get the appropriate tokenizer for the LLM model."""
        try:
            model_name = (
                getattr(self.llm_model.model, "model", None)
                or getattr(self.llm_model.model, "model_name", None)
                or "gpt-4o-mini"
            )  # fallback
            return tiktoken.encoding_for_model(model_name).encode
        except Exception as e:
            logger.warning(
                f"Could not get tokenizer for LLM model, using cl100k_base: {e}"
            )
            return tiktoken.get_encoding("cl100k_base").encode

    def _get_embedding_tokenizer(self):
        """Get the appropriate tokenizer for the embedding model."""
        try:
            model_name = (
                getattr(self.embedding_model.model, "model_name", None)
                or getattr(self.embedding_model.model, "model", None)
                or "text-embedding-ada-002"
            )  # fallback
            return tiktoken.encoding_for_model(model_name).encode
        except Exception as e:
            logger.warning(
                f"Could not get tokenizer for embedding model, using cl100k_base: {e}"
            )
            return tiktoken.get_encoding("cl100k_base").encode

    def reset_counts(self) -> None:
        """Reset all token counts to zero."""
        if self.llm_token_counter:
            self.llm_token_counter.reset_counts()
        self.embedding_token_counter.reset_counts()

    def get_token_counts(self) -> Dict[str, int]:
        """
        Get current token counts for both LLM and embedding operations.

        Returns:
            Dictionary containing token counts for different operations
        """
        llm_prompt_tokens = (
            self.llm_token_counter.prompt_llm_token_count
            if self.llm_token_counter
            else 0
        )
        llm_completion_tokens = (
            self.llm_token_counter.completion_llm_token_count
            if self.llm_token_counter
            else 0
        )
        llm_total_tokens = (
            self.llm_token_counter.total_llm_token_count
            if self.llm_token_counter
            else 0
        )
        embedding_tokens = self.embedding_token_counter.total_embedding_token_count
        total_tokens = llm_total_tokens + embedding_tokens

        logger.debug(
            f"Token counts - LLM prompt: {llm_prompt_tokens}, "
            f"LLM completion: {llm_completion_tokens}, "
            f"LLM total: {llm_total_tokens}, "
            f"Embedding: {embedding_tokens}, "
            f"Total: {total_tokens}"
        )

        return {
            "llm_prompt_tokens": llm_prompt_tokens,
            "llm_completion_tokens": llm_completion_tokens,
            "llm_total_tokens": llm_total_tokens,
            "embedding_tokens": embedding_tokens,
            "total_tokens": total_tokens,
        }

    def get_cost(self) -> float:
        """
        Get current costs based on token usage and configured pricing.

        Returns:
            Total cost as a float
        """
        counts = self.get_token_counts()

        llm_input_cost = (
            counts["llm_prompt_tokens"] / 1000
        ) * self.llm_input_price_per_1k
        llm_output_cost = (
            counts["llm_completion_tokens"] / 1000
        ) * self.llm_output_price_per_1k
        embedding_cost = (
            counts["embedding_tokens"] / 1000
        ) * self.embedding_price_per_1k

        total_cost = llm_input_cost + llm_output_cost + embedding_cost

        logger.info(
            f"Cost calculation - LLM input: ${llm_input_cost:.6f}, "
            f"LLM output: ${llm_output_cost:.6f}, "
            f"Embedding: ${embedding_cost:.6f}, "
            f"Total: ${total_cost:.6f}"
        )

        return total_cost


@contextmanager
def token_counter_context(
    user_id: str,
    embedding_model: PricedModel,
    llm_model: Optional[PricedModel] = None,
) -> Iterable[TokenCounter]:
    """
    Context manager for token counting operations with pricing support.

    This context manager provides a thread-safe way to track token usage across
    vector store and chat engine operations.

    Args:
        user_id: The ID of the user for logging token usage
        embedding_model: The embedding model to track tokens for
        llm_model: The LLM model to track tokens for (optional)

    Yields:
        TokenCounter: The token counter instance with callback manager
    """
    logger.info(
        f"Creating token counter for user {user_id} - LLM model: {llm_model is not None}"
    )
    counter = TokenCounter(embedding_model, llm_model)

    counter.reset_counts()
    logger.debug(
        f"Token counter created with callback manager: {counter.callback_manager}"
    )

    try:
        yield counter
    finally:
        cost = counter.get_cost()
        cost_type = "chat" if llm_model else "embedding"
        logger.info(
            f"User {user_id} used ${cost:.6f} estimated {cost_type} model cost."
        )
