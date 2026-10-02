"""Example using LLM Router with fallback providers.

========================================================================================================================
Name:         examples/03_router_with_fallbacks.py
Description:  Demonstrating automatic fallback to secondary provider
Project:      Pygenai
Date:         2026-10-02 18:59:23
Status:       Development

Copyright ©2026 All rights reserved.
========================================================================================================================
"""

from __future__ import annotations

import asyncio
import os

from pygenai.llm.base import Message, ProviderConfig, RetryConfig
from pygenai.llm.callbacks import CostTracker
from pygenai.llm.router import LLMRouter

# Load API keys from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")


async def main() -> None:
    """Run router with fallback example."""
    # Create primary provider configuration (OpenAI)
    primary_config = ProviderConfig(
        name="openai",
        api_key=OPENAI_API_KEY or "sk-test",
        model="gpt-4o-mini",
        timeout=10,
        retry_config=RetryConfig(
            max_retries=2,
            initial_delay=1.0,
        ),
    )

    # Create fallback provider configurations
    fallback_configs = [
        ProviderConfig(
            name="anthropic",
            api_key=ANTHROPIC_API_KEY or "sk-ant-test",
            model="claude-3-5-sonnet-20241022",
            timeout=10,
        ),
        ProviderConfig(
            name="ollama",
            model="llama3",
            base_url=OLLAMA_API_BASE,
            timeout=30,
        ),
    ]

    # Create router
    router = LLMRouter(primary_config, fallback_configs)

    # Display provider configuration
    print("📋 Router Configuration:")
    info = router.get_provider_info()
    print(f"   Primary: {info['primary']['name']} ({info['primary']['model']})")
    print(f"   Fallbacks: {len(info['fallbacks'])}")
    for fb in info["fallbacks"]:
        print(f"      - {fb['name']} ({fb['model']})")

    # Create cost tracker
    tracker = CostTracker()

    # Prepare messages
    messages = [
        Message(role="system", content="You are a helpful AI assistant."),
        Message(role="user", content="What is the importance of error handling in software?"),
    ]

    # Generate response (will fallback if primary fails)
    print("\n🚀 Generating response with automatic fallback...")
    try:
        response = await router.generate(messages)

        # Record the call for cost tracking
        tracker.record_call(response)

        # Display results
        print(f"\n📝 Response from {response.provider}/{response.model}:")
        print(f"   {response.content[:200]}...\n")
        print(f"💰 Cost: ${response.cost:.6f}")
        print(f"📊 Tokens: {response.usage.prompt_tokens} prompt + {response.usage.completion_tokens} completion")
        print(f"📍 Provider used: {response.provider}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
