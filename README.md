# Agent Service

Python service that runs the conversational agent layer for the monorepo.

## Purpose

- Orchestrates AI-agent interactions
- Integrates with MCP tools and upstream services
- Exposes an HTTP interface for local development and container runtime

## Location in the Monorepo

- Source code: `apps/agent/src/observe_agent`
- Service entrypoint: `apps/agent/src/__main__.py`
- Shared library dependency: `libs/observe_core`

## Requirements

- Python 3.13
- `uv`

## Setup

```bash
cd apps/agent
uv sync
```

## Run Locally

```bash
cd apps/agent
PYTHONPATH=src uv run python src/__main__.py
```

Default local endpoint:

- `http://127.0.0.1:8123`

## Docker Build

```bash
cd apps/agent
make docker-build
```

## Notes

- This project uses a local path dependency to `observe_core` in `libs/observe_core`.
- Docker/compose deployment is centralized in `infra/` at repo root.
