# Memory Package Examples

This directory contains practical examples of using the Pygenai Memory package.

## Running the Examples

From the project root (`libs/memory`):

```bash
# Buffer Memory
uv run examples/buffer_memory_example.py

# Window Memory
uv run examples/window_memory_example.py

# Summarized Memory
uv run examples/summarized_memory_example.py

# Persistence Adapter
uv run examples/persistence_adapter_example.py
```

## Examples Overview

### 1. Buffer Memory Example
Demonstrates simple sequential conversation history storage using `BufferMemory`.

**Use case**: Short conversations where you need to keep all messages without any trimming.

### 2. Window Memory Example
Shows how `WindowMemory` maintains a sliding context window, automatically trimming old messages.

**Use case**: Long-running conversations where you need to keep recent context within token limits.

### 3. Summarized Memory Example
Illustrates automatic compression using `SummarizedMemory`. Old messages are condensed into summaries when token threshold is exceeded.

**Use case**: Very long conversations where you want to preserve history through summaries while keeping recent context intact.

### 4. Persistence Adapter Example
Demonstrates saving and loading conversation state using `InMemoryAdapter` (other adapters: RedisAdapter, PostgreSQLAdapter).

**Use case**: Persisting conversation state across sessions or to external storage.

## Next Steps

- Integrate memory with your LangGraph agents
- Connect to Redis or PostgreSQL for production use
- Use Elasticsearch for semantic search over past conversations
- Implement custom summarizers for domain-specific compression

See the main [README.md](../README.md) for comprehensive documentation.
