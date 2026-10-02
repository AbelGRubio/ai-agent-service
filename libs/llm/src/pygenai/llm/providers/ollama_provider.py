"""Ollama provider implementation.

========================================================================================================================
Name:         genai/llm/providers/ollama_provider.py
Description:  Ollama LLM provider for local model inference using LiteLLM
Project:      Pygenai
Date:         2026-10-02 18:59:23
Status:       Development

Copyright ©2026 All rights reserved.
========================================================================================================================
"""

from __future__ import annotations

from typing import Any

import litellm

from pygenai.llm.base import LLMProvider, LLMResponse, Message, MessageUsage, ProviderConfig
from pygenai.llm.exceptions import ConfigurationError, InvalidResponseError, ProviderError


class OllamaProvider(LLMProvider):
    """Ollama LLM provider for local inference."""

    DEFAULT_MODELS = [
        "llama3",
        "llama2",
        "mistral",
        "neural-chat",
        "starling-lm",
        "orca-mini",
    ]

    def __init__(self, config: ProviderConfig) -> None:
        """Initialize Ollama provider.

        Args:
            config: Provider configuration.

        Raises:
            ConfigurationError: If configuration is invalid.
        """
        super().__init__(config)
        self.validate_config()
        self.base_url = config.base_url or "http://localhost:11434"

    def validate_config(self) -> bool:
        """Validate Ollama configuration.

        Returns:
            bool: True if valid.

        Raises:
            ConfigurationError: If configuration is invalid.
        """
        if not self.config.model:
            raise ConfigurationError("Ollama provider requires 'model' to be specified")
        return True

    async def generate(self, messages: list[Message], **kwargs: Any) -> LLMResponse:
        """Generate response using Ollama.

        Args:
            messages: List of messages.
            **kwargs: Additional parameters.

        Returns:
            LLMResponse: Unified response.

        Raises:
            ProviderError: If generation fails.
        """
        try:
            formatted_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

            response = litellm.completion(
                model=f"ollama/{self.config.model}",
                messages=formatted_messages,
                api_base=self.base_url,
                timeout=self.config.timeout,
                num_retries=self.config.retry_config.max_retries,
                **kwargs,
            )

            if not response or not hasattr(response, "choices"):
                raise InvalidResponseError("ollama", "Empty or malformed response")

            content = response.choices[0].message.content
            usage = MessageUsage(
                prompt_tokens=getattr(response.usage, "prompt_tokens", 0),
                completion_tokens=getattr(response.usage, "completion_tokens", 0),
            )

            return LLMResponse(
                content=content,
                model=self.config.model,
                provider="ollama",
                usage=usage,
                cost=0.0,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "api_base": self.base_url,
                    "raw_response": str(response),
                },
            )

        except Exception as e:
            raise ProviderError("ollama", str(e), e)

    def get_available_models(self) -> list[str]:
        """Get available Ollama models.

        Returns:
            list[str]: List of default model names (note: actual availability depends on local setup).
        """
        return self.DEFAULT_MODELS
