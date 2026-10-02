"""Azure OpenAI provider implementation.

========================================================================================================================
Name:         genai/llm/providers/azure_provider.py
Description:  Azure OpenAI LLM provider using LiteLLM
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

from pygenai.llm.base import LLMProvider, LLMResponse, Message, MessageUsage, ProviderConfig
from pygenai.llm.exceptions import AuthenticationError, ConfigurationError, InvalidResponseError, ProviderError


class AzureOpenAIProvider(LLMProvider):
    """Azure OpenAI LLM provider implementation."""

    def __init__(self, config: ProviderConfig) -> None:
        """Initialize Azure OpenAI provider.

        Args:
            config: Provider configuration.

        Raises:
            ConfigurationError: If configuration is invalid.
        """
        super().__init__(config)
        self.validate_config()
        self.api_key = config.api_key or os.getenv("AZURE_API_KEY")
        if not self.api_key:
            raise AuthenticationError("azure", "AZURE_API_KEY not provided in config or environment")

        self.api_base = config.base_url or os.getenv("AZURE_API_BASE")
        if not self.api_base:
            raise AuthenticationError("azure", "AZURE_API_BASE not provided in config or environment")

        self.api_version = os.getenv("AZURE_API_VERSION", "2024-02-15-preview")

    def validate_config(self) -> bool:
        """Validate Azure OpenAI configuration.

        Returns:
            bool: True if valid.

        Raises:
            ConfigurationError: If configuration is invalid.
        """
        if not self.config.model:
            raise ConfigurationError("Azure OpenAI provider requires 'model' (deployment name) to be specified")
        return True

    async def generate(self, messages: list[Message], **kwargs: Any) -> LLMResponse:
        """Generate response using Azure OpenAI.

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
                model=f"azure/{self.config.model}",
                messages=formatted_messages,
                api_key=self.api_key,
                api_base=self.api_base,
                api_version=self.api_version,
                timeout=self.config.timeout,
                num_retries=self.config.retry_config.max_retries,
                **kwargs,
            )

            if not response or not hasattr(response, "choices"):
                raise InvalidResponseError("azure", "Empty or malformed response")

            content = response.choices[0].message.content
            usage = MessageUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
            )

            cost = litellm.completion_cost(
                model=f"azure/{self.config.model}",
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
            )

            return LLMResponse(
                content=content,
                model=self.config.model,
                provider="azure",
                usage=usage,
                cost=cost,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "raw_response": str(response),
                },
            )

        except Exception as e:
            raise ProviderError("azure", str(e), e)

    def get_available_models(self) -> list[str]:
        """Get available Azure OpenAI models (deployments).

        Returns:
            list[str]: List of deployment names configured in Azure.
        """
        return [self.config.model] if self.config.model else []
