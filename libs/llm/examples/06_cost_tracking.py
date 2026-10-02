"""Example demonstrating cost tracking and auditing.

========================================================================================================================
Name:         examples/06_cost_tracking.py
Description:  Tracking and auditing LLM API call costs
Project:      Pygenai
Date:         2026-10-02 18:59:23
Status:       Development

Copyright ©2026 All rights reserved.
========================================================================================================================
"""

from __future__ import annotations

import asyncio
import os

from pygenai.llm.base import Message, ProviderConfig
from pygenai.llm.callbacks import CostTracker
from pygenai.llm.providers import OpenAIProvider, AnthropicProvider

# Load API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


async def make_api_call(provider_config: ProviderConfig) -> tuple:
    """Make a single API call and return response and provider info.

    Args:
        provider_config: Provider configuration.

    Returns:
        tuple: (response, provider_instance)
    """
    if provider_config.name == "openai":
        provider = OpenAIProvider(provider_config)
    elif provider_config.name == "anthropic":
        provider = AnthropicProvider(provider_config)
    else:
        raise ValueError(f"Unsupported provider: {provider_config.name}")

    messages = [
        Message(role="system", content="You are a helpful assistant."),
        Message(role="user", content="Summarize machine learning in 2 sentences."),
    ]

    response = await provider.generate(messages)
    return response, provider


async def main() -> None:
    """Run cost tracking example."""
    # Create cost tracker with logging
    tracker = CostTracker(log_file="/tmp/llm_costs.jsonl")

    # Define providers to test
    providers_to_test = []

    if OPENAI_API_KEY:
        providers_to_test.append(
            ProviderConfig(
                name="openai",
                api_key=OPENAI_API_KEY,
                model="gpt-4o-mini",
            )
        )

    if ANTHROPIC_API_KEY:
        providers_to_test.append(
            ProviderConfig(
                name="anthropic",
                api_key=ANTHROPIC_API_KEY,
                model="claude-3-5-sonnet-20241022",
            )
        )

    if not providers_to_test:
        print("❌ No API keys found. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY")
        return

    print(f"🚀 Testing {len(providers_to_test)} providers...\n")

    # Make API calls and track costs
    for config in providers_to_test:
        try:
            print(f"📞 Calling {config.name}/{config.model}...")
            response, provider = await make_api_call(config)

            # Record the call
            tracker.record_call(response, request_id=f"req_{config.name}_001")

            print(f"   ✅ Success: ${response.cost:.6f}")

        except Exception as e:
            print(f"   ❌ Failed: {e}")

    # Display comprehensive cost summary
    print("\n" + "=" * 80)
    print("💰 COST AUDIT REPORT")
    print("=" * 80)

    summary = tracker.get_summary()

    print(f"\n📊 Overall Statistics:")
    print(f"   Total API calls: {summary['total_calls']}")
    print(f"   Total cost: ${summary['total_cost_usd']:.6f}")
    print(f"   Average cost per call: ${summary['average_cost_per_call']:.6f}")
    print(f"   Total tokens used: {summary['total_tokens']}")

    print(f"\n💵 Cost Breakdown by Provider:")
    for provider, cost in summary["cost_by_provider"].items():
        print(f"   {provider}: ${cost:.6f}")

    print(f"\n📈 Token Usage by Provider:")
    for provider, tokens in summary["tokens_by_provider"].items():
        print(f"   {provider}:")
        print(f"      Prompt tokens: {tokens['prompt']}")
        print(f"      Completion tokens: {tokens['completion']}")

    print(f"\n📁 Cost log file: /tmp/llm_costs.jsonl")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
