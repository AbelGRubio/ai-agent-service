"""OpenAI provider implementation.

========================================================================================================================
Name:         genai/llm/providers/openai_provider.py
Description:  OpenAI LLM provider using LiteLLM
Project:      Pygenai
Date:         2026-10-02 18:59:23
Status:       Development

Copyright ©2026 All rights reserved.
========================================================================================================================
"""

from __future__ import annotations

import os
from typing import Any

import litellm

from ..base import LLMProvider, LLMResponse, Message, MessageUsage, ProviderConfig
from ..exceptions import AuthenticationError, ConfigurationError, InvalidResponseError, ProviderError


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider implementation."""

    AVAILABLE_MODELS = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
    ]

    def __init__(self, config: ProviderConfig) -> None:
        """Initialize OpenAI provider.

        Args:
            config: Provider configuration.

        Raises:
            ConfigurationError: If configuration is invalid.
        """
        super().__init__(config)
        self.validate_config()
        self.api_key = config.api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise AuthenticationError("openai", "OPENAI_API_KEY not provided in config or environment")

    def validate_config(self) -> bool:
        """Validate OpenAI configuration.

        Returns:
            bool: True if valid.

        Raises:
            ConfigurationError: If configuration is invalid.
        """
        if not self.config.model:
            raise ConfigurationError("OpenAI provider requires 'model' to be specified")
        if self.config.model not in self.AVAILABLE_MODELS:
            raise ConfigurationError(f"Model '{self.config.model}' not available. Available: {self.AVAILABLE_MODELS}")
        return True

    async def generate(self, messages: list[Message], **kwargs: Any) -> LLMResponse:
        """Generate response using OpenAI.

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
                model=f"openai/{self.config.model}",
                messages=formatted_messages,
                api_key=self.api_key,
                timeout=self.config.timeout,
                num_retries=self.config.retry_config.max_retries,
                **kwargs,
            )

            if not response or not hasattr(response, "choices"):
                raise InvalidResponseError("openai", "Empty or malformed response")

            content = response.choices[0].message.content
            usage = MessageUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
            )

            cost = litellm.completion_cost(
                model=f"openai/{self.config.model}",
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
            )

            return LLMResponse(
                content=content,
                model=self.config.model,
                provider="openai",
                usage=usage,
                cost=cost,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "raw_response": str(response),
                },
            )

        except Exception as e:
            raise ProviderError("openai", str(e), e)

    def get_available_models(self) -> list[str]:
        """Get available OpenAI models.

        Returns:
            list[str]: List of model names.
        """
        return self.AVAILABLE_MODELS
