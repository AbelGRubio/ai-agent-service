"""Tests for cost tracking module.

========================================================================================================================
Name:         tests/test_cost_tracker.py
Description:  Unit tests for cost tracking and audit logging
Project:      Pygenai
Date:         2026-10-02 18:59:23
Status:       Development

Copyright ©2026 All rights reserved.
========================================================================================================================
"""

from __future__ import annotations

import pytest

from genai.llm.base import LLMResponse, MessageUsage
from genai.llm.callbacks import CostTracker, CostRecord


def test_cost_record_creation() -> None:
    """Test creating a CostRecord instance."""
    record = CostRecord(
        provider="openai",
        model="gpt-4o",
        prompt_tokens=10,
        completion_tokens=20,
        cost_usd=0.05,
    )
    assert record.provider == "openai"
    assert record.model == "gpt-4o"
    assert record.prompt_tokens == 10
    assert record.completion_tokens == 20
    assert record.total_tokens == 30
    assert record.cost_usd == 0.05


def test_cost_record_to_dict() -> None:
    """Test converting CostRecord to dictionary."""
    record = CostRecord(
        provider="openai",
        model="gpt-4o",
        prompt_tokens=10,
        completion_tokens=20,
        cost_usd=0.05,
    )
    data = record.to_dict()
    assert data["provider"] == "openai"
    assert data["model"] == "gpt-4o"
    assert data["cost_usd"] == 0.05


def test_cost_tracker_initialization() -> None:
    """Test CostTracker initialization."""
    tracker = CostTracker()
    assert len(tracker.records) == 0
    assert tracker.get_total_cost() == 0.0


def test_cost_tracker_record_call(cost_tracker: CostTracker) -> None:
    """Test recording an API call in CostTracker."""
    response = LLMResponse(
        content="Test response",
        model="gpt-4o",
        provider="openai",
        usage=MessageUsage(prompt_tokens=10, completion_tokens=20),
        cost=0.05,
    )
    record = cost_tracker.record_call(response)
    assert record.provider == "openai"
    assert record.model == "gpt-4o"
    assert record.cost_usd == 0.05


def test_cost_tracker_total_cost(cost_tracker: CostTracker) -> None:
    """Test calculating total cost."""
    response1 = LLMResponse(
        content="Response 1",
        model="gpt-4o",
        provider="openai",
        usage=MessageUsage(prompt_tokens=10, completion_tokens=20),
        cost=0.05,
    )
    response2 = LLMResponse(
        content="Response 2",
        model="gpt-4o",
        provider="openai",
        usage=MessageUsage(prompt_tokens=15, completion_tokens=25),
        cost=0.08,
    )
    cost_tracker.record_call(response1)
    cost_tracker.record_call(response2)
    assert cost_tracker.get_total_cost() == 0.13


def test_cost_tracker_by_provider(cost_tracker: CostTracker) -> None:
    """Test cost tracking by provider."""
    response1 = LLMResponse(
        content="Response 1",
        model="gpt-4o",
        provider="openai",
        usage=MessageUsage(prompt_tokens=10, completion_tokens=20),
        cost=0.05,
    )
    response2 = LLMResponse(
        content="Response 2",
        model="claude-3",
        provider="anthropic",
        usage=MessageUsage(prompt_tokens=15, completion_tokens=25),
        cost=0.08,
    )
    cost_tracker.record_call(response1)
    cost_tracker.record_call(response2)

    cost_by_provider = cost_tracker.get_cost_by_provider()
    assert cost_by_provider["openai"] == 0.05
    assert cost_by_provider["anthropic"] == 0.08


def test_cost_tracker_summary(cost_tracker: CostTracker) -> None:
    """Test cost tracker summary generation."""
    response = LLMResponse(
        content="Test response",
        model="gpt-4o",
        provider="openai",
        usage=MessageUsage(prompt_tokens=10, completion_tokens=20),
        cost=0.05,
    )
    cost_tracker.record_call(response)

    summary = cost_tracker.get_summary()
    assert summary["total_calls"] == 1
    assert summary["total_cost_usd"] == 0.05
    assert summary["total_tokens"] == 30


def test_cost_tracker_reset(cost_tracker: CostTracker) -> None:
    """Test resetting cost tracker."""
    response = LLMResponse(
        content="Test response",
        model="gpt-4o",
        provider="openai",
        usage=MessageUsage(prompt_tokens=10, completion_tokens=20),
        cost=0.05,
    )
    cost_tracker.record_call(response)
    assert cost_tracker.get_total_cost() == 0.05

    cost_tracker.reset()
    assert cost_tracker.get_total_cost() == 0.0
    assert len(cost_tracker.records) == 0
