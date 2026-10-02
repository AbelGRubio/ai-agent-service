"""AWS Bedrock provider implementation.

========================================================================================================================
Name:         genai/llm/providers/bedrock_provider.py
Description:  AWS Bedrock LLM provider using LiteLLM
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


class BedrockProvider(LLMProvider):
    """AWS Bedrock LLM provider implementation."""

    AVAILABLE_MODELS = [
        "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        "us.anthropic.claude-3-5-haiku-20241022-v1:0",
        "us.anthropic.claude-3-opus-20250219-v1:0",
        "us.anthropic.claude-3-sonnet-20250229-v1:0",
    ]

    def __init__(self, config: ProviderConfig) -> None:
        """Initialize AWS Bedrock provider.

        Args:
            config: Provider configuration.

        Raises:
            ConfigurationError: If configuration is invalid.
        """
        super().__init__(config)
        self.validate_config()
        self.region = os.getenv("AWS_REGION_NAME", "us-east-1")

    def validate_config(self) -> bool:
        """Validate AWS Bedrock configuration.

        Returns:
            bool: True if valid.

        Raises:
            ConfigurationError: If configuration is invalid.
        """
        if not self.config.model:
            raise ConfigurationError("Bedrock provider requires 'model' to be specified")
        if self.config.model not in self.AVAILABLE_MODELS:
            raise ConfigurationError(
                f"Model '{self.config.model}' not available. Available: {self.AVAILABLE_MODELS}"
            )

        if not os.getenv("AWS_ACCESS_KEY_ID"):
            raise AuthenticationError("bedrock", "AWS_ACCESS_KEY_ID not found in environment")
        if not os.getenv("AWS_SECRET_ACCESS_KEY"):
            raise AuthenticationError("bedrock", "AWS_SECRET_ACCESS_KEY not found in environment")

        return True

    async def generate(self, messages: list[Message], **kwargs: Any) -> LLMResponse:
        """Generate response using AWS Bedrock.

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
                model=f"bedrock/{self.config.model}",
                messages=formatted_messages,
                region_name=self.region,
                timeout=self.config.timeout,
                num_retries=self.config.retry_config.max_retries,
                **kwargs,
            )

            if not response or not hasattr(response, "choices"):
                raise InvalidResponseError("bedrock", "Empty or malformed response")

            content = response.choices[0].message.content
            usage = MessageUsage(
                prompt_tokens=getattr(response.usage, "prompt_tokens", 0),
                completion_tokens=getattr(response.usage, "completion_tokens", 0),
            )

            cost = litellm.completion_cost(
                model=f"bedrock/{self.config.model}",
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
            )

            return LLMResponse(
                content=content,
                model=self.config.model,
                provider="bedrock",
                usage=usage,
                cost=cost,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "region": self.region,
                    "raw_response": str(response),
                },
            )

        except Exception as e:
            raise ProviderError("bedrock", str(e), e)

    def get_available_models(self) -> list[str]:
        """Get available AWS Bedrock models.

        Returns:
            list[str]: List of model names.
        """
        return self.AVAILABLE_MODELS
