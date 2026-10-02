"""Basic example of using OpenAI provider.

========================================================================================================================
Name:         examples/01_basic_openai.py
Description:  Simple example of generating text with OpenAI
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
from pygenai.llm.providers import OpenAIProvider

# Load API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")


async def main() -> None:
    """Run basic OpenAI example."""
    # Create provider configuration
    config = ProviderConfig(
        name="openai",
        api_key=OPENAI_API_KEY,
        model="gpt-4o-mini",
        timeout=30,
    )

    # Create provider instance
    provider = OpenAIProvider(config)

    # Create cost tracker
    tracker = CostTracker()

    # Prepare messages
    messages = [
        Message(role="system", content="You are a helpful assistant."),
        Message(role="user", content="What are the main principles of machine learning?"),
    ]

    # Generate response
    print("🚀 Generating response from OpenAI...")
    response = await provider.generate(messages)

    # Record the call for cost tracking
    tracker.record_call(response)

    # Display results
    print(f"\n📝 Response from {response.provider}/{response.model}:")
    print(f"   {response.content}\n")
    print(f"💰 Cost: ${response.cost:.6f}")
    print(f"📊 Tokens: {response.usage.prompt_tokens} prompt + {response.usage.completion_tokens} completion")
    print(f"\n📈 Cumulative Statistics:")
    print(f"   Total cost: ${tracker.get_total_cost():.6f}")
    print(f"   Total calls: {len(tracker.records)}")


if __name__ == "__main__":
    asyncio.run(main())
