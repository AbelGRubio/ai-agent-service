"""Example using local Ollama provider.

========================================================================================================================
Name:         examples/05_ollama_local.py
Description:  Using local Ollama for LLM inference
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
from pygenai.llm.providers import OllamaProvider

# Load configuration from environment
OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")


async def main() -> None:
    """Run Ollama local provider example."""
    print(f"📡 Connecting to Ollama at {OLLAMA_API_BASE}")
    print(f"🤖 Using model: {OLLAMA_MODEL}\n")

    # Create provider configuration
    config = ProviderConfig(
        name="ollama",
        model=OLLAMA_MODEL,
        base_url=OLLAMA_API_BASE,
        timeout=120,  # Local inference may take longer
    )

    # Create provider instance
    provider = OllamaProvider(config)

    # Create cost tracker (local models have $0 cost)
    tracker = CostTracker()

    # Prepare messages
    messages = [
        Message(role="system", content="You are a helpful assistant running locally."),
        Message(role="user", content="What makes a good software architecture?"),
    ]

    # Generate response
    print("🚀 Generating response from local Ollama...")
    response = await provider.generate(messages)

    # Record the call for cost tracking
    tracker.record_call(response)

    # Display results
    print(f"\n📝 Response from {response.provider}/{response.model}:")
    print(f"   {response.content}\n")
    print(f"💰 Cost: ${response.cost:.6f} (local model, no API costs)")
    print(f"📊 Tokens: {response.usage.prompt_tokens} prompt + {response.usage.completion_tokens} completion")
    print(f"✅ Total free inference calls: {len(tracker.records)}")

    # Show available models
    print(f"\n📚 Available Ollama models (default list):")
    for model in provider.get_available_models()[:5]:
        print(f"   - {model}")
    print(f"   ... and more (check your local Ollama installation)")


if __name__ == "__main__":
    asyncio.run(main())
