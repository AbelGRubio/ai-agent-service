# Pygenai  AI Agent Development Guidelines

This document is the **behavioral mandate** for AI agents and developers working on the Pygenai MCP repository. It defines the canonical workflows, architecture rules, quality gates, and hard constraints.

**CRITICAL**: Before making any code change, you MUST also read [CONVENTIONS.md](CONVENTIONS.md) — it contains the tech stack, code conventions, and structural reference that all agents are required to follow.

---

## 🚀 Core Workflows

### 1. Environment Setup & Onboarding
- **Initial setup**: Always run `make setup` first
- **Portability**: All scripts and Makefile targets must be POSIX-compliant (WSL, Linux, macOS). Use Python for complex logic — never long bash in Makefiles.
- **Credential safety**: Artifactory/Bitbucket tokens live in `.env` and are backed up to `.env.backup` on `make clean`. Never commit these files.

### 2. Monorepo Architecture
- **Agent package layout**: Agents are organized into focused modules (examples: `file`, `rag`, `memory`, `prompts`). Each agent module is a self-contained package that includes its implementation code, skill definitions, lightweight README, and tests. Typical responsibilities:
  - `file`: adapters and helpers for file I/O and storage integrations (local, S3, DB, GridFS).
  - `rag`: retrieval-augmented generation pipelines, retrievers, and index wiring.
  - `memory`: long-term state, vector stores, session persistence, and memory primitives.
  - `prompts`: canonical prompt templates, prompt-management utilities, and prompt testing artifacts.
  Agents should be discoverable under the repo's agents area (e.g., `.agents/` or `src/agents/`) and follow the repo's packaging and test conventions.
- **Dev deps**: path-based (`path = "../.."`, editable). **Production**: switch to Artifactory registry index.

### 3. Quality Assurance (CI)
- **Always run `make ci` before proposing any change.** Includes:
  - `checkmake` — Makefile linter (strict target line limits).
  - `ruff` — Python linter (complexity ≤ 10, line length 120).
  - `pyrefly` — Type checker.
  - `pytest` — Full test suite.

### 5. Core Agnostic Architecture
`src/observability_core` must remain cloud-agnostic.

- `core/` is for business logic and orchestration only.
- Cloud SDK usage and API calls belong in `core/aws/`, `core/gcp/`, `core/azure/`.
- Keep backward compatibility via re-export shims when moving modules.


---

## 🛠 Technical Standards

Keep this file minimal. Use skills as source of detail:

- [pygenai-conventions](.agents/skills/pygenai-conventions/SKILL.md): coding standards, Makefile patterns, env/datamodel flow, toolchain rules.
- [add-file-header](.agents/skills/add-file-header/SKILL.md): Skill for adding headers to files.

Non-negotiable baseline:

- Never use `pip`; always `uv`.
- Never use `print()`; use `get_logger`/`rich`.
- Never use shell scripts; use Make + Python CLI.
- Never use `sed -i`; use portable `sed ... > file.tmp && mv file.tmp file`.
- In runtime modules, use `get_settings()` as the canonical settings source; avoid direct `AppSettings()` construction outside bootstrap/generation paths.

---

## ✅ Quality Gates

Before suggesting or applying any change, verify it passes:

1. `ruff check` — linting (complexity ≤ 10, all rule groups in `pyproject.toml`).
2. `pyrefly check` — type checking.
3. `pytest` — all tests pass.
4. `checkmake` — all Makefile targets within line limits.

---


---

## 🚫 Hard Constraints

- **NEVER** use `print()` — use `get_logger`/`rich`.
- **NEVER** use `pip` — always `uv`.
- **NEVER** use `sed -i` — use the portable `sed ... > file.tmp && mv file.tmp file` pattern.
- **NEVER** use shell scripts — use Make targets + Python CLI only.
- **NEVER** commit `.env`, `.env.backup`, or any secrets/tokens.
- **NEVER** add unnecessary abstractions — keep complexity minimal.
- **NEVER** add error handling for scenarios that cannot happen.
- **NEVER** hardcode paths to package files — use `$(wildcard)` dynamic resolution.
- **NEVER** instantiate `AppSettings()` directly in runtime/business modules; use `get_settings()` instead.
- **NEVER** run git write commands (`commit`, `push`, `rebase`, `reset`, `merge`) — these are reserved for the human developer.
- **NEVER** run any `aws` CLI command — AWS credentials are not available in the VS Code terminal; commands will fail or block.
- **NEVER** read `.git/config`, `~/.aws/credentials`, or any file containing remote credentials.
- **NEVER** auto-compact conversation or make irreversible state changes — if token budget is low, ask the user first.
