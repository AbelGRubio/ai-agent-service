"""Custom exceptions for LLM module.

========================================================================================================================
Name:         genai/llm/exceptions.py
Description:  Custom exception classes for LLM operations, provider errors, and rate limiting
Project:      Pygenai
Date:         2026-10-02 18:59:23
Status:       Development

Copyright ©2026 All rights reserved.
========================================================================================================================
"""

from __future__ import annotations


class LLMException(Exception):
    """Base exception for all LLM-related errors."""

    pass


class ProviderError(LLMException):
    """Exception raised when a provider fails."""

    def __init__(self, provider: str, message: str, original_error: Exception | None = None) -> None:
        self.provider = provider
        self.message = message
        self.original_error = original_error
        super().__init__(f"Provider {provider} error: {message}")


class RateLimitError(LLMException):
    """Exception raised when rate limit is exceeded (429 error)."""

    def __init__(self, provider: str, retry_after: int | None = None) -> None:
        self.provider = provider
        self.retry_after = retry_after
        message = f"Rate limit exceeded for provider {provider}"
        if retry_after:
            message += f" (retry after {retry_after}s)"
        super().__init__(message)


class AuthenticationError(LLMException):
    """Exception raised when authentication fails."""

    def __init__(self, provider: str, message: str = "Invalid credentials") -> None:
        self.provider = provider
        super().__init__(f"Authentication failed for provider {provider}: {message}")


class ModelNotFoundError(LLMException):
    """Exception raised when a model is not available."""

    def __init__(self, model: str, provider: str | None = None) -> None:
        self.model = model
        self.provider = provider
        msg = f"Model '{model}' not found"
        if provider:
            msg += f" for provider '{provider}'"
        super().__init__(msg)


class NoAvailableProvidersError(LLMException):
    """Exception raised when no providers are available (all fallbacks exhausted)."""

    def __init__(self, attempted_providers: list[str]) -> None:
        self.attempted_providers = attempted_providers
        super().__init__(f"No available providers. Attempted: {', '.join(attempted_providers)}")


class ConfigurationError(LLMException):
    """Exception raised when configuration is invalid."""

    def __init__(self, message: str) -> None:
        super().__init__(f"Configuration error: {message}")


class InvalidResponseError(LLMException):
    """Exception raised when provider response is invalid or malformed."""

    def __init__(self, provider: str, message: str) -> None:
        self.provider = provider
        super().__init__(f"Invalid response from {provider}: {message}")
