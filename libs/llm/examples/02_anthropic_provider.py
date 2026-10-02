"""Example using multiple LLM providers with Anthropic.

========================================================================================================================
Name:         examples/02_anthropic_provider.py
Description:  Using Anthropic Claude model
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
from pygenai.llm.providers import AnthropicProvider

# Load API key from environment
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable not set")


async def main() -> None:
    """Run Anthropic provider example."""
    # Create provider configuration
    config = ProviderConfig(
        name="anthropic",
        api_key=ANTHROPIC_API_KEY,
        model="claude-3-5-sonnet-20241022",
        timeout=30,
    )

    # Create provider instance
    provider = AnthropicProvider(config)

    # Create cost tracker
    tracker = CostTracker()

    # Prepare messages
    messages = [
        Message(role="system", content="You are a Python expert who explains concepts clearly."),
        Message(role="user", content="Explain decorators in Python with a simple example."),
    ]

    # Generate response
    print("🚀 Generating response from Anthropic Claude...")
    response = await provider.generate(messages)

    # Record the call for cost tracking
    tracker.record_call(response)

    # Display results
    print(f"\n📝 Response from {response.provider}/{response.model}:")
    print(f"   {response.content}\n")
    print(f"💰 Cost: ${response.cost:.6f}")
    print(f"📊 Tokens: {response.usage.prompt_tokens} prompt + {response.usage.completion_tokens} completion")

    # Show available models
    print(f"\n📚 Available Anthropic models:")
    for model in provider.get_available_models():
        print(f"   - {model}")


if __name__ == "__main__":
    asyncio.run(main())
