"""Pytest configuration and fixtures.

========================================================================================================================
Name:         tests/conftest.py
Description:  Shared fixtures and configuration for tests
Project:      Pygenai
Date:         2026-10-02 18:59:23
Status:       Development

Copyright ©2026 All rights reserved.
========================================================================================================================
"""

from __future__ import annotations

import pytest

from genai.llm.base import Message, MessageUsage, ProviderConfig, RetryConfig
from genai.llm.callbacks import CostTracker


@pytest.fixture
def retry_config() -> RetryConfig:
    """Create a test retry configuration.

    Returns:
        RetryConfig: Test retry configuration.
    """
    return RetryConfig(
        max_retries=2,
        initial_delay=0.1,
        max_delay=1.0,
        exponential_base=2.0,
    )


@pytest.fixture
def provider_config(retry_config: RetryConfig) -> ProviderConfig:
    """Create a test provider configuration.

    Returns:
        ProviderConfig: Test provider configuration.
    """
    return ProviderConfig(
        name="openai",
        api_key="sk-test-key",
        model="gpt-4o",
        timeout=10,
        retry_config=retry_config,
    )


@pytest.fixture
def cost_tracker() -> CostTracker:
    """Create a cost tracker instance.

    Returns:
        CostTracker: Cost tracker instance.
    """
    return CostTracker()


@pytest.fixture
def sample_messages() -> list[Message]:
    """Create sample messages for testing.

    Returns:
        list[Message]: List of sample messages.
    """
    return [
        Message(role="system", content="You are a helpful assistant."),
        Message(role="user", content="Hello, how are you?"),
    ]


@pytest.fixture
def sample_message_usage() -> MessageUsage:
    """Create sample message usage for testing.

    Returns:
        MessageUsage: Sample usage data.
    """
    return MessageUsage(
        prompt_tokens=10,
        completion_tokens=20,
    )
