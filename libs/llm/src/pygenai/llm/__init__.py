"""Py LLM Module - Unified LLM Provider Abstraction.

========================================================================================================================
Name:         /llm/__init__.py
Description:  Main package exports for the LLM module
Project:      Py
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
from pygenai.llm.litellm_provider import LiteLLMProvider

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
    "LiteLLMProvider",
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
