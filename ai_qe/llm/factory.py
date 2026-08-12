import os

from ai_qe.config.ai_config import AIConfig

from ai_qe.llm.base import LLMProvider
from ai_qe.llm.ollama_provider import OllamaProvider
from ai_qe.llm.openai_provider import OpenAIProvider

from ai_qe.config.ai_config import (
        AIConfig,
        AIProvider,)

def create_provider() -> LLMProvider:
    config = AIConfig.from_env()

    print(f"Using provider: {config.provider}")
    print(f"Using model: {config.model}")
    print(f"Using AI configuration: {config}")
    
    if  config.provider is AIProvider.OLLAMA:
        return OllamaProvider(
            model=config.model,
        )

    if config.provider is AIProvider.OPENAI:
        return OpenAIProvider(
            model=config.model,
        )

    raise ValueError(
        f"Unsupported provider: {config.provider}"
    )