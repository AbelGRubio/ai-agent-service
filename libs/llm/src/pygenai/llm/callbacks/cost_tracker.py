"""Cost tracking and callback handlers.

========================================================================================================================
Name:         genai/llm/callbacks/cost_tracker.py
Description:  Cost calculation and audit logging for LLM API calls
Project:      Pygenai
Date:         2026-10-02 18:59:23
Status:       Development

Copyright ©2026 All rights reserved.
========================================================================================================================
"""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from pygenai.llm.base import LLMResponse

logger = logging.getLogger(__name__)


@dataclass
class CostRecord:
    """Record of a single API call cost."""

    timestamp: datetime = field(default_factory=datetime.now)
    provider: str = ""
    model: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    request_id: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            dict: Dictionary representation of the cost record.
        """
        return {
            "timestamp": self.timestamp.isoformat(),
            "provider": self.provider,
            "model": self.model,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "cost_usd": self.cost_usd,
            "request_id": self.request_id,
        }


class CostTracker:
    """Track costs and usage across LLM API calls."""

    def __init__(self, log_file: str | Path | None = None) -> None:
        """Initialize cost tracker.

        Args:
            log_file: Optional file path for logging cost records.
        """
        self.log_file = Path(log_file) if log_file else None
        self.records: list[CostRecord] = []
        self.cost_by_provider: dict[str, float] = defaultdict(float)
        self.cost_by_model: dict[str, float] = defaultdict(float)
        self.tokens_by_provider: dict[str, dict[str, int]] = defaultdict(lambda: {"prompt": 0, "completion": 0})

    def record_call(self, response: LLMResponse, request_id: str | None = None) -> CostRecord:
        """Record an LLM API call.

        Args:
            response: LLMResponse object with usage and cost data.
            request_id: Optional request identifier for tracking.

        Returns:
            CostRecord: The recorded cost information.
        """
        record = CostRecord(
            timestamp=datetime.now(),
            provider=response.provider,
            model=response.model,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens,
            cost_usd=response.cost,
            request_id=request_id,
        )

        self.records.append(record)
        self.cost_by_provider[response.provider] += response.cost
        self.cost_by_model[response.model] += response.cost
        self.tokens_by_provider[response.provider]["prompt"] += response.usage.prompt_tokens
        self.tokens_by_provider[response.provider]["completion"] += response.usage.completion_tokens

        logger.info(
            f"API Call recorded: {response.provider}/{response.model} - "
            f"Cost: ${response.cost:.6f}, Tokens: {response.usage.total_tokens}"
        )

        if self.log_file:
            self._write_record_to_file(record)

        return record

    def _write_record_to_file(self, record: CostRecord) -> None:
        """Write cost record to log file.

        Args:
            record: Cost record to log.
        """
        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_file, "a") as f:
                f.write(json.dumps(record.to_dict()) + "\n")
        except Exception as e:
            logger.error(f"Failed to write cost record to file: {e}")

    def get_total_cost(self) -> float:
        """Get total cost across all calls.

        Returns:
            float: Total cost in USD.
        """
        return sum(record.cost_usd for record in self.records)

    def get_cost_by_provider(self) -> dict[str, float]:
        """Get cost breakdown by provider.

        Returns:
            dict: Provider -> cost mapping.
        """
        return dict(self.cost_by_provider)

    def get_cost_by_model(self) -> dict[str, float]:
        """Get cost breakdown by model.

        Returns:
            dict: Model -> cost mapping.
        """
        return dict(self.cost_by_model)

    def get_token_summary(self) -> dict[str, dict[str, int]]:
        """Get token usage summary.

        Returns:
            dict: Token usage by provider.
        """
        return dict(self.tokens_by_provider)

    def get_summary(self) -> dict:
        """Get comprehensive cost and usage summary.

        Returns:
            dict: Summary statistics.
        """
        total_cost = self.get_total_cost()
        total_tokens = sum(
            stats["prompt"] + stats["completion"] for stats in self.tokens_by_provider.values()
        )

        return {
            "total_calls": len(self.records),
            "total_cost_usd": total_cost,
            "average_cost_per_call": total_cost / len(self.records) if self.records else 0.0,
            "total_tokens": total_tokens,
            "cost_by_provider": self.get_cost_by_provider(),
            "cost_by_model": self.get_cost_by_model(),
            "tokens_by_provider": self.get_token_summary(),
        }

    def reset(self) -> None:
        """Reset all tracking data."""
        self.records = []
        self.cost_by_provider.clear()
        self.cost_by_model.clear()
        self.tokens_by_provider.clear()
        logger.info("Cost tracker reset")
