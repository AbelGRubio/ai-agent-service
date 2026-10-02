"""Anthropic provider implementation.

========================================================================================================================
Name:         genai/llm/providers/anthropic_provider.py
Description:  Anthropic Claude LLM provider using LiteLLM
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


class AnthropicProvider(LLMProvider):
    """Anthropic (Claude) LLM provider implementation."""

    AVAILABLE_MODELS = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20250219",
        "claude-3-sonnet-20250229",
        "claude-3-haiku-20250307",
    ]

    def __init__(self, config: ProviderConfig) -> None:
        """Initialize Anthropic provider.

        Args:
            config: Provider configuration.

        Raises:
            ConfigurationError: If configuration is invalid.
        """
        super().__init__(config)
        self.validate_config()
        self.api_key = config.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise AuthenticationError("anthropic", "ANTHROPIC_API_KEY not provided in config or environment")

    def validate_config(self) -> bool:
        """Validate Anthropic configuration.

        Returns:
            bool: True if valid.

        Raises:
            ConfigurationError: If configuration is invalid.
        """
        if not self.config.model:
            raise ConfigurationError("Anthropic provider requires 'model' to be specified")
        if self.config.model not in self.AVAILABLE_MODELS:
            raise ConfigurationError(f"Model '{self.config.model}' not available. Available: {self.AVAILABLE_MODELS}")
        return True

    async def generate(self, messages: list[Message], **kwargs: Any) -> LLMResponse:
        """Generate response using Anthropic.

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
                model=f"anthropic/{self.config.model}",
                messages=formatted_messages,
                api_key=self.api_key,
                timeout=self.config.timeout,
                num_retries=self.config.retry_config.max_retries,
                **kwargs,
            )

            if not response or not hasattr(response, "choices"):
                raise InvalidResponseError("anthropic", "Empty or malformed response")

            content = response.choices[0].message.content
            usage = MessageUsage(
                prompt_tokens=getattr(response.usage, "prompt_tokens", 0),
                completion_tokens=getattr(response.usage, "completion_tokens", 0),
            )

            cost = litellm.completion_cost(
                model=f"anthropic/{self.config.model}",
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
            )

            return LLMResponse(
                content=content,
                model=self.config.model,
                provider="anthropic",
                usage=usage,
                cost=cost,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "raw_response": str(response),
                },
            )

        except Exception as e:
            raise ProviderError("anthropic", str(e), e)

    def get_available_models(self) -> list[str]:
        """Get available Anthropic models.

        Returns:
            list[str]: List of model names.
        """
        return self.AVAILABLE_MODELS
