# Pygenai Memory

![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Package](https://img.shields.io/badge/Package-pygenai--memory-8A2BE2)
![Tests](https://img.shields.io/badge/Tests-pytest-4B8BBE?logo=pytest&logoColor=white)

A lightweight and extensible memory layer for AI agents. It supports short-term memory, sliding-window retention, summarization, persistent storage adapters, and semantic retrieval for conversational workflows.

## Why use it

- Short-term memory for sequential conversation history
- Sliding-window retention to prevent context overflow
- Automatic summarization for long-running sessions
- Persistence adapters for local, Redis, and PostgreSQL storage
- Semantic search with Elasticsearch
- Token-aware utilities for context budgeting

## Installation

- Install from the package index:
  uv add pygenai-memory
- Or install from this repository:
  cd libs/memory
  uv sync --all-extras

## Package overview

The package includes the following building blocks:

- BufferMemory: keeps the full conversation history
- WindowMemory: keeps only the most recent context
- SummarizedMemory: compresses older segments into summaries
- InMemoryAdapter: volatile in-process storage for tests and local usage
- RedisAdapter: fast session persistence for active workloads
- PostgreSQLAdapter: durable relational storage
- ElasticsearchMemory: semantic search over stored messages
- Message, ConversationState, SummaryRecord: core data structures
- TokenCounter: token estimation utilities

## Examples

The runnable examples live in the examples directory and are intentionally kept outside the package README for readability.

- examples/buffer_memory_example.py — sequential memory usage
- examples/window_memory_example.py — sliding-window retention
- examples/summarized_memory_example.py — automatic summarization
- examples/persistence_adapter_example.py — adapter-based storage patterns

## Core components

### Memory stores

- BufferMemory: best for short conversations that require full history
- WindowMemory: recommended for production agents with token limits
- SummarizedMemory: ideal for long-lived sessions that need context compression

### Persistence adapters

- InMemoryAdapter: quick development and tests
- RedisAdapter: high-throughput session storage with optional TTL
- PostgreSQLAdapter: durable relational persistence

### Semantic layer

- ElasticsearchMemory: indexes messages and enables similarity search for prior context

## Development

- Setup:
  cd libs/memory
  uv sync --all-extras
- Run tests:
  uv run pytest
- Linting:
  uv run ruff check .
- Type checking:
  uv run pyrefly check
- Full quality gate:
  make ci

## Contributing

Contributions are welcome. Please keep the documentation concise, keep examples in the examples directory, and validate changes with the package test and quality checks.

## License

MIT

## References

- LangGraph documentation
- Tiktoken documentation
- Redis documentation
- PostgreSQL documentation
- Elasticsearch documentation
