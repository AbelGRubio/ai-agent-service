"""Tests for LLM Router.

========================================================================================================================
Name:         tests/test_router.py
Description:  Unit tests for router and fallback logic
Project:      Pygenai
Date:         2026-10-02 18:59:23
Status:       Development

Copyright ©2026 All rights reserved.
========================================================================================================================
"""

from __future__ import annotations

import pytest

from genai.llm.base import ProviderConfig, RetryConfig
from genai.llm.exceptions import ConfigurationError
from genai.llm.router import LLMRouter


def test_router_initialization() -> None:
    """Test LLMRouter initialization."""
    primary_config = ProviderConfig(
        name="openai",
        api_key="sk-test",
        model="gpt-4o",
    )
    router = LLMRouter(primary_config)
    assert router.primary_config.name == "openai"
    assert len(router.fallback_configs) == 0


def test_router_with_fallbacks() -> None:
    """Test LLMRouter with fallback providers."""
    primary_config = ProviderConfig(
        name="openai",
        api_key="sk-test",
        model="gpt-4o",
    )
    fallback_config1 = ProviderConfig(
        name="anthropic",
        api_key="sk-ant-test",
        model="claude-3-5-sonnet-20241022",
    )
    fallback_config2 = ProviderConfig(
        name="ollama",
        model="llama3",
        base_url="http://localhost:11434",
    )
    router = LLMRouter(primary_config, [fallback_config1, fallback_config2])
    assert len(router.fallback_configs) == 2
    assert router.fallback_configs[0].name == "anthropic"
    assert router.fallback_configs[1].name == "ollama"


def test_router_invalid_provider() -> None:
    """Test LLMRouter with invalid provider."""
    config = ProviderConfig(
        name="invalid-provider",
        api_key="test",
        model="test",
    )
    with pytest.raises(ValueError):
        LLMRouter(config)


def test_router_get_provider_info() -> None:
    """Test getting provider information from router."""
    primary_config = ProviderConfig(
        name="openai",
        api_key="sk-test",
        model="gpt-4o",
    )
    fallback_config = ProviderConfig(
        name="anthropic",
        api_key="sk-ant-test",
        model="claude-3-5-sonnet-20241022",
    )
    router = LLMRouter(primary_config, [fallback_config])
    info = router.get_provider_info()

    assert info["primary"]["name"] == "openai"
    assert info["primary"]["model"] == "gpt-4o"
    assert "available_models" in info["primary"]
    assert len(info["fallbacks"]) == 1
    assert info["fallbacks"][0]["name"] == "anthropic"


def test_router_retry_config_preservation() -> None:
    """Test that retry config is preserved in router."""
    retry_config = RetryConfig(
        max_retries=5,
        initial_delay=2.0,
        max_delay=120.0,
    )
    primary_config = ProviderConfig(
        name="openai",
        api_key="sk-test",
        model="gpt-4o",
        retry_config=retry_config,
    )
    router = LLMRouter(primary_config)
    assert router.primary_config.retry_config.max_retries == 5
    assert router.primary_config.retry_config.initial_delay == 2.0
