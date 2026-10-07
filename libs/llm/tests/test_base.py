"""Tests for LLM base module.

========================================================================================================================
Name:         tests/test_base.py
Description:  Unit tests for base models and interfaces
Project:      Pygenai
Date:         2026-10-02 18:59:23
Status:       Development

Copyright ©2026 All rights reserved.
========================================================================================================================
"""

from __future__ import annotations

import pytest

from genai.llm.base import LLMResponse, Message, MessageUsage, ProviderConfig, RetryConfig
from genai.llm.exceptions import ConfigurationError


def test_message_creation() -> None:
    """Test creating a Message instance."""
    msg = Message(role="user", content="Test message")
    assert msg.role == "user"
    assert msg.content == "Test message"


def test_message_usage_calculation() -> None:
    """Test MessageUsage total token calculation."""
    usage = MessageUsage(prompt_tokens=10, completion_tokens=20)
    assert usage.total_tokens == 30


def test_message_usage_default_total() -> None:
    """Test MessageUsage auto-calculates total."""
    usage = MessageUsage(prompt_tokens=5, completion_tokens=15)
    assert usage.total_tokens == 20


def test_llm_response_creation() -> None:
    """Test creating an LLMResponse instance."""
    usage = MessageUsage(prompt_tokens=10, completion_tokens=20)
    response = LLMResponse(
        content="Test response",
        model="gpt-4o",
        provider="openai",
        usage=usage,
        cost=0.05,
    )
    assert response.content == "Test response"
    assert response.model == "gpt-4o"
    assert response.provider == "openai"
    assert response.usage.total_tokens == 30
    assert response.cost == 0.05


def test_provider_config_creation(retry_config: RetryConfig) -> None:
    """Test creating a ProviderConfig instance."""
    config = ProviderConfig(
        name="openai",
        api_key="sk-test",
        model="gpt-4o",
        timeout=30,
        retry_config=retry_config,
    )
    assert config.name == "openai"
    assert config.api_key == "sk-test"
    assert config.model == "gpt-4o"
    assert config.timeout == 30
    assert config.retry_config.max_retries == 2


def test_retry_config_defaults() -> None:
    """Test RetryConfig default values."""
    config = RetryConfig()
    assert config.max_retries == 3
    assert config.initial_delay == 1.0
    assert config.max_delay == 60.0
    assert 429 in config.retry_on
    assert 500 in config.retry_on


def test_provider_config_extra_params() -> None:
    """Test ProviderConfig with extra parameters."""
    extra = {"temperature": 0.7, "top_p": 0.9}
    config = ProviderConfig(
        name="anthropic",
        api_key="sk-test",
        model="claude-3-opus",
        extra_params=extra,
    )
    assert config.extra_params["temperature"] == 0.7
    assert config.extra_params["top_p"] == 0.9
