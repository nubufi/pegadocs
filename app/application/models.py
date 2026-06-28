from dataclasses import dataclass
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.llms.utils import LLMType


@dataclass
class PricedModel:
    model: BaseEmbedding | LLMType
    input_price_per_1k_tokens: float
    output_price_per_1k_tokens: float
