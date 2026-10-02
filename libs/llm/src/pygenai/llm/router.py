"""LLM Router with fallback and retry logic.

========================================================================================================================
Name:         genai/llm/router.py
Description:  Intelligent router for managing LLM provider fallbacks and retries
Project:      Pygenai
Date:         2026-10-02 18:59:23
Status:       Development

Copyright ©2026 All rights reserved.
========================================================================================================================
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from pygenai.llm.base import FallbackConfig, LLMProvider, LLMResponse, Message, ProviderConfig, RetryConfig
from pygenai.llm.exceptions import NoAvailableProvidersError, ProviderError, RateLimitError
from pygenai.llm.providers import AnthropicProvider, AzureOpenAIProvider, BedrockProvider, OllamaProvider, OpenAIProvider

logger = logging.getLogger(__name__)


class LLMRouter:
    """Intelligent router for LLM requests with fallback and retry logic."""

    PROVIDER_MAPPING = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "azure": AzureOpenAIProvider,
        "bedrock": BedrockProvider,
        "ollama": OllamaProvider,
    }

    def __init__(
        self,
        primary_config: ProviderConfig,
        fallback_configs: list[ProviderConfig] | None = None,
    ) -> None:
        """Initialize LLM Router.

        Args:
            primary_config: Primary provider configuration.
            fallback_configs: List of fallback provider configurations (optional).
        """
        self.primary_config = primary_config
        self.fallback_configs = fallback_configs or []
        self.primary_provider = self._create_provider(primary_config)
        self.fallback_providers = [self._create_provider(cfg) for cfg in self.fallback_configs]

    def _create_provider(self, config: ProviderConfig) -> LLMProvider:
        """Create a provider instance from configuration.

        Args:
            config: Provider configuration.

        Returns:
            LLMProvider: Instantiated provider.

        Raises:
            ValueError: If provider type is unknown.
        """
        provider_class = self.PROVIDER_MAPPING.get(config.name.lower())
        if not provider_class:
            raise ValueError(f"Unknown provider: {config.name}")
        return provider_class(config)

    async def generate(self, messages: list[Message], **kwargs: Any) -> LLMResponse:
        """Generate response with automatic fallback.

        Args:
            messages: List of messages.
            **kwargs: Additional parameters.

        Returns:
            LLMResponse: Response from primary or fallback provider.

        Raises:
            NoAvailableProvidersError: If all providers fail.
        """
        providers_to_try = [(self.primary_provider, self.primary_config)] + list(
            zip(self.fallback_providers, self.fallback_configs)
        )
        attempted_providers = []
        last_error = None

        for provider, config in providers_to_try:
            attempted_providers.append(config.name)
            try:
                logger.info(f"Attempting to generate with provider: {config.name}")
                response = await self._execute_with_retry(provider, messages, config.retry_config, **kwargs)
                logger.info(f"Successfully generated response from {config.name}")
                return response

            except RateLimitError as e:
                logger.warning(f"Rate limit exceeded for {config.name}, trying fallback...")
                last_error = e
                continue

            except ProviderError as e:
                logger.warning(f"Provider error from {config.name}: {e}, trying fallback...")
                last_error = e
                continue

            except Exception as e:
                logger.error(f"Unexpected error from {config.name}: {e}")
                last_error = e
                continue

        raise NoAvailableProvidersError(attempted_providers)

    async def _execute_with_retry(
        self, provider: LLMProvider, messages: list[Message], retry_config: RetryConfig, **kwargs: Any
    ) -> LLMResponse:
        """Execute provider call with retry logic.

        Args:
            provider: LLM provider instance.
            messages: List of messages.
            retry_config: Retry configuration.
            **kwargs: Additional parameters.

        Returns:
            LLMResponse: Response from provider.

        Raises:
            ProviderError: If all retries fail.
        """
        delay = retry_config.initial_delay
        last_error = None

        for attempt in range(retry_config.max_retries + 1):
            try:
                return await provider.generate(messages, **kwargs)

            except RateLimitError as e:
                last_error = e
                if attempt < retry_config.max_retries:
                    wait_time = retry_config.max_delay if e.retry_after is None else min(e.retry_after, retry_config.max_delay)
                    logger.warning(f"Rate limit, retry attempt {attempt + 1}/{retry_config.max_retries}. Waiting {wait_time}s")
                    await asyncio.sleep(wait_time)
                    delay = min(delay * retry_config.exponential_base, retry_config.max_delay)

            except ProviderError as e:
                last_error = e
                if attempt < retry_config.max_retries:
                    logger.warning(f"Provider error, retry attempt {attempt + 1}/{retry_config.max_retries}. Waiting {delay}s")
                    await asyncio.sleep(delay)
                    delay = min(delay * retry_config.exponential_base, retry_config.max_delay)

        raise last_error or ProviderError(provider.name, "Max retries exceeded")

    def get_provider_info(self) -> dict[str, Any]:
        """Get information about configured providers.

        Returns:
            dict: Information about primary and fallback providers.
        """
        return {
            "primary": {
                "name": self.primary_config.name,
                "model": self.primary_config.model,
                "available_models": self.primary_provider.get_available_models(),
            },
            "fallbacks": [
                {
                    "name": cfg.name,
                    "model": cfg.model,
                    "available_models": provider.get_available_models(),
                }
                for cfg, provider in zip(self.fallback_configs, self.fallback_providers)
            ],
        }
