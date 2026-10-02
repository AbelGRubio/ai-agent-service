"""Example using Azure OpenAI provider.

========================================================================================================================
Name:         examples/04_azure_openai.py
Description:  Using Azure OpenAI deployment
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
from pygenai.llm.providers import AzureOpenAIProvider

# Load configuration from environment
AZURE_API_KEY = os.getenv("AZURE_API_KEY")
AZURE_API_BASE = os.getenv("AZURE_API_BASE")
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4")

if not AZURE_API_KEY or not AZURE_API_BASE:
    raise ValueError("AZURE_API_KEY and AZURE_API_BASE environment variables must be set")


async def main() -> None:
    """Run Azure OpenAI provider example."""
    # Create provider configuration
    config = ProviderConfig(
        name="azure",
        api_key=AZURE_API_KEY,
        model=AZURE_DEPLOYMENT_NAME,  # This is the deployment name in Azure
        base_url=AZURE_API_BASE,
        timeout=30,
    )

    # Create provider instance
    provider = AzureOpenAIProvider(config)

    # Create cost tracker
    tracker = CostTracker()

    # Prepare messages
    messages = [
        Message(role="system", content="You are an expert in cloud computing."),
        Message(role="user", content="Explain the benefits of Azure OpenAI service."),
    ]

    # Generate response
    print("🚀 Generating response from Azure OpenAI...")
    response = await provider.generate(messages)

    # Record the call for cost tracking
    tracker.record_call(response)

    # Display results
    print(f"\n📝 Response from {response.provider}/{response.model}:")
    print(f"   {response.content}\n")
    print(f"💰 Cost: ${response.cost:.6f}")
    print(f"📊 Tokens: {response.usage.prompt_tokens} prompt + {response.usage.completion_tokens} completion")
    print(f"\n🔧 Deployment: {AZURE_DEPLOYMENT_NAME}")
    print(f"📍 API Base: {AZURE_API_BASE}")


if __name__ == "__main__":
    asyncio.run(main())
