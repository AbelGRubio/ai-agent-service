"""Tests for LLM providers.

========================================================================================================================
Name:         tests/test_providers.py
Description:  Unit tests for provider implementations
Project:      Pygenai
Date:         2026-10-02 18:59:23
Status:       Development

Copyright ©2026 All rights reserved.
========================================================================================================================
"""

from __future__ import annotations

import pytest

from genai.llm.base import ProviderConfig, RetryConfig
from genai.llm.exceptions import AuthenticationError, ConfigurationError
from genai.llm.providers import AnthropicProvider, AzureOpenAIProvider, BedrockProvider, OllamaProvider, OpenAIProvider


def test_openai_provider_validation() -> None:
    """Test OpenAI provider configuration validation."""
    config = ProviderConfig(
        name="openai",
        api_key="sk-test",
        model="gpt-4o",
    )
    provider = OpenAIProvider(config)
    assert provider.validate_config() is True


def test_openai_provider_invalid_model() -> None:
    """Test OpenAI provider with invalid model."""
    config = ProviderConfig(
        name="openai",
        api_key="sk-test",
        model="invalid-model",
    )
    with pytest.raises(ConfigurationError):
        OpenAIProvider(config)


def test_openai_provider_missing_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test OpenAI provider without API key."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    config = ProviderConfig(
        name="openai",
        api_key=None,
        model="gpt-4o",
    )
    with pytest.raises(AuthenticationError):
        OpenAIProvider(config)


def test_openai_provider_available_models() -> None:
    """Test getting available OpenAI models."""
    config = ProviderConfig(
        name="openai",
        api_key="sk-test",
        model="gpt-4o",
    )
    provider = OpenAIProvider(config)
    models = provider.get_available_models()
    assert "gpt-4o" in models
    assert "gpt-4o-mini" in models


def test_anthropic_provider_validation() -> None:
    """Test Anthropic provider configuration validation."""
    config = ProviderConfig(
        name="anthropic",
        api_key="sk-ant-test",
        model="claude-3-5-sonnet-20241022",
    )
    provider = AnthropicProvider(config)
    assert provider.validate_config() is True


def test_anthropic_provider_available_models() -> None:
    """Test getting available Anthropic models."""
    config = ProviderConfig(
        name="anthropic",
        api_key="sk-ant-test",
        model="claude-3-5-sonnet-20241022",
    )
    provider = AnthropicProvider(config)
    models = provider.get_available_models()
    assert "claude-3-5-sonnet-20241022" in models


def test_azure_provider_validation() -> None:
    """Test Azure OpenAI provider configuration validation."""
    config = ProviderConfig(
        name="azure",
        api_key="azure-test-key",
        model="gpt-4",
        base_url="https://test.openai.azure.com",
    )
    provider = AzureOpenAIProvider(config)
    assert provider.validate_config() is True


def test_azure_provider_missing_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test Azure provider without base URL."""
    monkeypatch.delenv("AZURE_API_BASE", raising=False)
    config = ProviderConfig(
        name="azure",
        api_key="azure-test-key",
        model="gpt-4",
        base_url=None,
    )
    with pytest.raises(AuthenticationError):
        AzureOpenAIProvider(config)


def test_bedrock_provider_validation() -> None:
    """Test AWS Bedrock provider configuration validation."""
    config = ProviderConfig(
        name="bedrock",
        model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    )
    # This should fail because AWS credentials are not available
    with pytest.raises(AuthenticationError):
        BedrockProvider(config)


def test_ollama_provider_validation() -> None:
    """Test Ollama provider configuration validation."""
    config = ProviderConfig(
        name="ollama",
        model="llama3",
        base_url="http://localhost:11434",
    )
    provider = OllamaProvider(config)
    assert provider.validate_config() is True


def test_ollama_provider_available_models() -> None:
    """Test getting available Ollama models."""
    config = ProviderConfig(
        name="ollama",
        model="llama3",
        base_url="http://localhost:11434",
    )
    provider = OllamaProvider(config)
    models = provider.get_available_models()
    assert "llama3" in models
    assert "mistral" in models


def test_provider_config_with_custom_timeout() -> None:
    """Test provider configuration with custom timeout."""
    config = ProviderConfig(
        name="openai",
        api_key="sk-test",
        model="gpt-4o",
        timeout=60,
    )
    provider = OpenAIProvider(config)
    assert provider.config.timeout == 60


def test_provider_config_with_retry_config() -> None:
    """Test provider configuration with custom retry settings."""
    retry_config = RetryConfig(max_retries=5, initial_delay=2.0)
    config = ProviderConfig(
        name="openai",
        api_key="sk-test",
        model="gpt-4o",
        retry_config=retry_config,
    )
    provider = OpenAIProvider(config)
    assert provider.config.retry_config.max_retries == 5
    assert provider.config.retry_config.initial_delay == 2.0
