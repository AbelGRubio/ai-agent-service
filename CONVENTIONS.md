# Pygenai MCP - Tech Stack & Code Conventions

This document is the **technical reference** for developers and AI agents working on the Pygenai MCP repository. It covers the stack, project structure, code conventions, and Makefile patterns. For workflows, architecture rules, and hard constraints, see [AGENTS.md](AGENTS.md).

---

## 🐍 Tech Stack

### Core dependencies (always prefer these)

| Library | Purpose | Usage                                                                 |
|---|---|-----------------------------------------------------------------------|
| **`fastmcp`** | MCP server framework | Use `FastMCP`; tools are decorated with `@mcp.tool()`                 |
| **`typer`** | CLI commands | Create sub-apps with `typer.Typer()`, register with `app.add_typer()` |
| **`logging`** (stdlib, via `logging`) | Logging | `from logging import getLogger` — never `print()`                     |
| **`rich`** | Terminal output | Use `rich.console.Console` and `rich.panel.Panel` for panels/tables   |
| **`pydantic`** | Data models & settings | Use `BaseSettings` for config classes with env prefix                 |

### Dev toolchain

| Tool | Role | Key config |
|---|---|---|
| **`uv`** | Package manager | `uv run`, `uv sync`, `uv add` — never `pip` |
| **`ruff`** | Linter + formatter | Line length 120, complexity ≤ 10, Google docstrings |
| **`pyrefly`** | Type checker | Strict — always annotate all args and return types |
| **`pytest`** + `pytest-asyncio` + `pytest-cov` | Tests | Full async support, coverage reports |
| **`pre-commit`** | Git hooks | Runs ruff + checks before every commit |
| **`checkmake`** | Makefile linter | Strict target line limits — keep targets short |

### Python version
- **Python 3.13 strictly** (`requires-python = ">=3.13,<3.14"`).
- Use modern syntax: `X | Y` unions, `match` statements, `tomllib`, etc.
- Avoid `typing` module aliases that have `collections.abc` equivalents.


---

## ✍️ Code Conventions

### File header (required for every new Python file)

```pythonf
"""Module title.

========================================================================================================================
Name:         path/filename.py
Description:  Brief description
Project:      Pygenai
Date:         YYYY-MM-DD HH:MM:SS
Status:       Development

Copyright ©2026 All rights reserved.
========================================================================================================================
"""
```

### Docstrings — Google style

```python
def my_function(param: str) -> bool:
    """Short one-line summary.

    Args:
        param: Description of param.

    Returns:
        Description of return value.
    """
```

### Imports — isort order

```python
# 1. future
from __future__ import annotations

# 2. standard-library
import os
from collections.abc import Callable

# 3. third-party
from opentelemetry import trace
from pydantic import BaseSettings

# 4. first-party (pygenai)
from pygenai.core.logger import get_logger

# 5. local-folder
from .utils import helper
```

### Type annotations

- Always annotate **all** function arguments and return types.
- Use `from __future__ import annotations` only when needed for forward references.
- Prefer `collections.abc` over `typing` for `Callable`, `Iterator`, `Sequence`, etc.
- Use `X | Y` union syntax (Python 3.10+ style), not `Union[X, Y]`.
- Use `X | None` instead of `Optional[X]`.

### Logging

```python
from pygenai.core.logger import get_logger

logger = get_logger(__name__)

logger.info(f"Starting process: {my_var}")
logger.warning(f"Skipping step: {details}")
logger.error(f"Failed: {exc}")
```

### CLI commands (Typer)

```python
import typer
from logging import getLogger

app = typer.Typer(name="my-command", help="Short description.")
logger = getLogger(__name__)


@app.command()
def my_action(param: str = typer.Argument(..., help="Description.")) -> None:
    """Short one-line summary."""
    logger.info(f"Running my_action with {param}")
```

Register in `src/pygenai/core/cli.py`:
```python
from pygenai.my_module import app as my_app

main_app.add_typer(my_app)
```

### MCP tools (FastMCP)

```python
from fastmcp import FastMCP

mcp = FastMCP("pygenai-mcp")


@mcp.tool()
async def my_tool(query: str) -> str:
    """Tool description shown to the LLM client.

    Args:
        query: The input query.

    Returns:
        The result string.
    """
    ...
```

---

## 🔧 Makefile Patterns

### Philosophy
- **Short targets** — checkmake enforces line limits. Any logic beyond a few lines belongs in a Python script or CLI command.
- **No shell scripts** — everything is a Make target.
- **No `sed -i`** — use `sed "..." file > file.tmp && mv file.tmp file`.
- **Export vars** — always `export` so child processes inherit `.env` variables.



---

### Key differences vs production (`Dockerfile`)

| | `Dockerfile.local` | `Dockerfile` (production/AWS) |
|---|---|---|
| Platform | `--platform linux/amd64` (Rosetta 2 on Mac) | Native ARM64 (AWS Agent Core) |
| Cmd | `python app.py` | `uvicorn` / `opentelemetry-instrument` |
| Env | `--env-file .env` + `-e SERVER__HOST=0.0.0.0` | Injected by runtime |

### Why `--platform linux/amd64` in `Dockerfile.local`

Docker Desktop on Apple Silicon does not expose some newer ARMv9 CPU features
(SME2, SVE2p1, etc.) to Linux ARM64 containers. Libraries with Rust-compiled
binaries (e.g. `cryptography`) use those instructions → **SIGILL** (exit 132).
Running as `linux/amd64` under Rosetta 2 avoids this. Production ARM64 Linux
machines (AWS) expose all features natively — no issue there.

### `SERVER__HOST` override

The `.env` file typically has `SERVER__HOST=localhost`, which makes the server
bind only inside the container and become unreachable from the host. The
`docker run` command overrides it with `-e SERVER__HOST=0.0.0.0`.

### OTel warnings

Lines like `Failed to export logs to localhost:4317` are benign — there is no
OpenTelemetry collector running locally. They do not affect functionality.

---

## ⚙️ Settings & Configuration

Settings are composed from multiple Pydantic `BaseSettings` classes, each with a distinct env prefix:

| Class | File | Prefix | Purpose |
|---|---|---|---|
| `ServerConfig` | `core/settings/server.py` | `SERVER__` | Host, port, auth mode, CORS |
| `ApiSettings` | `core/settings/api.py` | `API__` | External API URLs, timeouts |
| *(generated)* | `core/env/datamodel.py` | varies | Auto-generated from `settings_definitions.yml` |

All configs are combined in `settings.py` via `get_settings()`.

---

## 🔐 Security

- Auth middleware is in `core/security/auth.py`.
- IDP adapters (Keycloak, Cognito, Authentik, Logto) live in `core/security/adapters/`.
- The active IDP is chosen at runtime via `SecurityManager` (`core/security/security_manager.py`).
- OAuth2/OIDC token validation is handled per-adapter — never implement custom crypto.

### Git Security (agent constraints)
The repository remote is configured with **split credentials**:
- **Fetch URL** carries a read-only token — pull/fetch work silently.
- **Push URL** carries no token — any push attempt will block waiting for credentials the agent cannot supply.

As an agent you MUST:
- **NEVER** execute `git commit`, `git push`, `git rebase`, `git reset`, `git merge`, `git push --force`, or any variant — using full path (`/usr/bin/git`), `command git`, `\git`, or any other bypass technique.
- **NEVER** modify or inspect the fetch or push remote URL (`git remote set-url`, `git remote -v`).
- **NEVER** call `git credential`, `git config credential.*`, or any command that reads, writes, or manipulates stored credentials.
- **NEVER** read `.git/config` to discover remote URLs or tokens.
- **ALLOWED**: Show the git command in a code block so the user can copy and run it manually in their external terminal.
- All write operations (commit, push, rebase) are the exclusive responsibility of the human developer.

### AWS Security (agent constraints)
AWS credentials are **never stored on disk** in this project. They are injected into the developer's external shell session only via `awsume` (short-lived STS tokens), and are not available in the VS Code terminal where the agent runs.

As an agent you MUST:
- **NEVER** run any `aws` CLI command — read or write, local or remote. The VS Code terminal has no AWS credentials; commands will fail or block.
- **NEVER** attempt to read `~/.aws/credentials`, `~/.aws/config`, or any file that may contain AWS keys.
- **NEVER** call `awsume`, `aws configure`, or `aws sts` to attempt credential discovery.
- **ALLOWED**: Show the `aws` or `awsume` command in a code block so the user can run it manually in their external terminal where credentials are available.

---

## 🖥 Developer Terminal Setup (one-time)

> Run all commands below in an **external terminal** (iTerm2 / macOS Terminal) — NOT in the VS Code integrated terminal.
> The agent only has access to the VS Code terminal; your external terminal is the secure boundary for all write operations.

### Git — split credentials (read fetch / prompt push)

```zsh
# 1. Set fetch URL with your read-only Bitbucket token
git remote set-url origin https://YOUR_USER:READ_ONLY_TOKEN@github.com/ORG/REPO.git

# 2. Set push URL without any token — git will prompt on every push
git remote set-url --push origin https://github.com/ORG/REPO.git

# 3. Disable local credential caching for push
git config --local credential.helper ""
```

After this setup:
- `git fetch` / `git pull` → silent, uses read-only token
- `git push` → VS Code Source Control panel or external terminal prompts for write token each time
- Token is never stored on disk for push

### Git — daily push workflow (external terminal only)

```zsh
# Stage and commit
git add -p
git commit -m "feat(GIAO-XX): short description"

# Push — enter your write token when prompted
git push origin feature/GIAO-XX-your-branch
# username: YOUR_BITBUCKET_USER
# password: YOUR_WRITE_TOKEN
```

### AWS — session activation (external terminal only)

```zsh
# Activate your AWS profile — credentials stay in this shell session only
awsume your-profile-name

# Verify
aws sts get-caller-identity

# Example: ECR login
aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin YOUR_ECR_URL
```

Credentials injected by `awsume` are shell environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SESSION_TOKEN`) — they exist only in that terminal session and expire automatically. The VS Code terminal never has them.
