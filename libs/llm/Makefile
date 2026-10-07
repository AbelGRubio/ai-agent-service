# =============================================================================
#                          Makefile - Pygenai LLM Module
#                          Author: AI Assistant
#                          Purpose: Development and testing workflow
# =============================================================================

.PHONY: help setup clean test lint format type-check ci install dev examples

# ─────────────────────────────────────────────────────────────────────────────
# Variables
# ─────────────────────────────────────────────────────────────────────────────
VENV := .venv
PYTHON := $(VENV)/bin/python
UV := uv
PROJECT_NAME := pygenai-llm

# ─────────────────────────────────────────────────────────────────────────────
# Help
# ─────────────────────────────────────────────────────────────────────────────
help:
	@echo "╔════════════════════════════════════════════════════════════════════╗"
	@echo "║                   $(PROJECT_NAME) - Makefile Help                  ║"
	@echo "╚════════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "Available targets:"
	@echo ""
	@echo "  setup              Initialize development environment"
	@echo "  install            Install dependencies"
	@echo "  dev                Install dev dependencies"
	@echo "  test               Run test suite"
	@echo "  test-coverage      Run tests with coverage report"
	@echo "  lint               Run ruff linter"
	@echo "  format             Format code with ruff"
	@echo "  type-check         Run pyrefly type checker"
	@echo "  ci                 Run full CI pipeline (lint, type-check, tests)"
	@echo "  examples           List available examples"
	@echo "  clean              Remove generated files and cache"
	@echo "  help               Show this help message"
	@echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Setup & Installation
# ─────────────────────────────────────────────────────────────────────────────
setup: clean install dev
	@echo "✅ Development environment setup complete"

install:
	@echo "📦 Installing dependencies..."
	$(UV) sync

dev: install
	@echo "🔧 Installing dev dependencies..."
	$(UV) sync --all-extras

# ─────────────────────────────────────────────────────────────────────────────
# Testing
# ─────────────────────────────────────────────────────────────────────────────
test:
	@echo "🧪 Running tests..."
	$(UV) run pytest tests/ -v

test-coverage:
	@echo "📊 Running tests with coverage..."
	$(UV) run pytest tests/ -v --cov=src/genai/llm --cov-report=html
	@echo "✅ Coverage report: htmlcov/index.html"

# ─────────────────────────────────────────────────────────────────────────────
# Code Quality
# ─────────────────────────────────────────────────────────────────────────────
lint:
	@echo "🔍 Linting with ruff..."
	$(UV) run ruff check src/ tests/ examples/

format:
	@echo "✨ Formatting code with ruff..."
	$(UV) run ruff format src/ tests/ examples/

type-check:
	@echo "🔎 Type checking with pyrefly..."
	$(UV) run pyrefly check src/

ci: lint type-check test
	@echo "✅ CI pipeline passed!"

# ─────────────────────────────────────────────────────────────────────────────
# Examples
# ─────────────────────────────────────────────────────────────────────────────
examples:
	@echo "📚 Available examples:"
	@echo ""
	@echo "  01_basic_openai.py"
	@echo "     Basic OpenAI text generation"
	@echo ""
	@echo "  02_anthropic_provider.py"
	@echo "     Using Anthropic Claude"
	@echo ""
	@echo "  03_router_with_fallbacks.py"
	@echo "     Automatic fallback to secondary provider"
	@echo ""
	@echo "  04_azure_openai.py"
	@echo "     Azure OpenAI deployment"
	@echo ""
	@echo "  05_ollama_local.py"
	@echo "     Local model inference (zero cost)"
	@echo ""
	@echo "  06_cost_tracking.py"
	@echo "     Comprehensive cost audit example"
	@echo ""
	@echo "Run examples with:"
	@echo "  OPENAI_API_KEY=sk-... $(UV) run examples/01_basic_openai.py"

# ─────────────────────────────────────────────────────────────────────────────
# Cleanup
# ─────────────────────────────────────────────────────────────────────────────
clean:
	@echo "🧹 Cleaning up..."
	rm -rf $(VENV) .pytest_cache .coverage htmlcov .ruff_cache __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".DS_Store" -delete
	@echo "✅ Cleanup complete"

.PHONY: help setup install dev test test-coverage lint format type-check ci examples clean
