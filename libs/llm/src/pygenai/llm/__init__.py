"""Pypygenai LLM Module - Unified LLM Provider Abstraction.

========================================================================================================================
Name:         pygenai/llm/__init__.py
Description:  Main package exports for the LLM module
Project:      Pypygenai
Date:         2026-10-02 18:59:23
Status:       Development

Copyright ©2026 All rights reserved.
========================================================================================================================
"""

from __future__ import annotations

from pygenai.llm.base import (
    FallbackConfig,
    LLMProvider,
    LLMResponse,
    Message,
    MessageUsage,
    ProviderConfig,
    RetryConfig,
)
from pygenai.llm.callbacks import CostRecord, CostTracker
from pygenai.llm.exceptions import (
    AuthenticationError,
    ConfigurationError,
    InvalidResponseError,
    LLMException,
    ModelNotFoundError,
    NoAvailableProvidersError,
    ProviderError,
    RateLimitError,
)
from pygenai.llm.providers import (
    AnthropicProvider,
    AzureOpenAIProvider,
    BedrockProvider,
    OllamaProvider,
    OpenAIProvider,
)
from pygenai.llm.router import LLMRouter

__all__ = [
    # Base models and interfaces
    "LLMProvider",
    "LLMResponse",
    "Message",
    "MessageUsage",
    "ProviderConfig",
    "RetryConfig",
    "FallbackConfig",
    # Providers
    "OpenAIProvider",
    "AnthropicProvider",
    "AzureOpenAIProvider",
    "BedrockProvider",
    "OllamaProvider",
    # Router
    "LLMRouter",
    # Callbacks
    "CostTracker",
    "CostRecord",
    # Exceptions
    "LLMException",
    "ProviderError",
    "RateLimitError",
    "AuthenticationError",
    "ModelNotFoundError",
    "NoAvailableProvidersError",
    "ConfigurationError",
    "InvalidResponseError",
]

__version__ = "0.1.0"
