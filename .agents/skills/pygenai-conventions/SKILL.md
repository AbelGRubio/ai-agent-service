---
name: pygenai-conventions
description: 'Pygenai tech stack, code conventions, and Makefile patterns. Use when writing Python code, adding CLI commands, defining MCP tools, editing Makefiles, adding dependencies, or reviewing code in this repo. Covers: fastmcp, typer, pydantic, uv, ruff, pyrefly, pytest, Python 3.13, type annotations, imports, docstrings, logging patterns.'
---

# Pygenai — Conventions Quick Reference

Full reference: [CONVENTIONS.md](../../../CONVENTIONS.md)

## Hard Constraints

- **NEVER** use `print()` — use `from pygenai_mcp.core.logger import get_logger`
- **NEVER** `pip` — always `uv`
- **NEVER** `sed -i` — use `sed "..." f > f.tmp && mv f.tmp f`
- **NEVER** `Union[X, Y]` or `Optional[X]` — use `X | Y` and `X | None`
- **NEVER** shell scripts — Make targets + Python CLI only
- **ALWAYS** use `get_settings()` as canonical settings source in runtime/business modules

## Git & AWS Security Constraints

**Git** — the remote is configured with split credentials:
- Fetch URL has a read-only token → pull/fetch work silently
- Push URL has no token → push will block; the agent cannot push
- **NEVER** execute `git commit`, `git push`, `git rebase`, `git reset`, `git merge` — including via full path (`/usr/bin/git`), `command git`, `\git`, or any other bypass
- **NEVER** modify or inspect remote URLs (`git remote set-url`, `git remote -v`)
- **NEVER** read `.git/config` or manipulate stored credentials
- **ALLOWED**: show git commands in a code block for the user to run manually in their external terminal

**AWS** — credentials are never on disk; they live only in the developer's external shell via `awsume`:
- **NEVER** run any `aws` CLI command — read or write; the VS Code terminal has no credentials
- **NEVER** read `~/.aws/credentials`, `~/.aws/config`, or call `awsume`/`aws configure`
- **ALLOWED**: show `aws`/`awsume` commands in a code block for the user to run in their external terminal

## Developer Terminal Setup (copy-paste — external terminal only)

> All commands below must be run in **iTerm2 / macOS Terminal**, never in the VS Code integrated terminal.

### One-time git split credential setup

```zsh
# Fetch with read-only token (silent pulls)
git remote set-url origin https://YOUR_USER:READ_ONLY_TOKEN@github.com/ORG/REPO.git

# Push with no token (prompts each time — write token never stored)
git remote set-url --push origin https://github.com/ORG/REPO.git

git config --local credential.helper ""
```

### Daily push workflow

```zsh
git add -p
git commit -m "feat(GIAO-XX): description"
git push origin feature/GIAO-XX-your-branch
```

## Stack at a Glance

| Need | Use |
|---|---|
| CLI | `typer.Typer()` + `app.add_typer()` |
| Logging | `get_logger(__name__)` from `pygenai_mcp.core.logger` |
| Terminal output | `rich.console.Console` / `rich.panel.Panel` |
| Settings | `get_settings()` in runtime modules; `AppSettings()` only in bootstrap/generation |
| Package manager | `uv run` / `uv sync` / `uv add` |
| Python version | **3.13 strictly** — use `X | Y`, `match`, `tomllib` |

## Type Annotations

```python
from __future__ import annotations  # only when needed for forward refs
from collections.abc import Callable, Sequence  # not from typing


def fn(x: str, cb: Callable[[str], bool]) -> str | None: ...
```

## Logging

```python
logger = get_logger(__name__)

logger.info(f"Starting: {value}")
logger.warning(f"Skipping: {details}")
logger.error(f"Failed: {exc}")
```

## CLI Command Pattern

```python
app = typer.Typer(name="my-command", help="Short description.")


@app.command()
def my_action(param: str = typer.Argument(..., help="Description.")) -> None:
    """Short summary."""
    logger.info(f"Running: {param}")
```
Register in `src/pygenai_mcp/core/cli.py` via `main_app.add_typer(my_app)`.

## Makefile Rules

- Keep targets short — checkmake enforces line limits
- Complex logic → `uv run pygenai-mcp ...` or `uv run scripts/...`
- Always `export` vars so child processes receive `.env`

## Quality Gates (run before any change)

```
make ci   # checkmake + ruff + pyrefly + pytest
```
