# =============================================================================
#                     			Makefile
#                  Author: Abel
#                  Created: 2025-2026
#                  Purpose: Development workflow
# =============================================================================

# ──────────────────────────────────────────────────────────────────────────────
#  Configuration & Variables
# ──────────────────────────────────────────────────────────────────────────────
ifneq (,$(wildcard .env))
    include .env
    export UV_INDEX_USERNAME UV_INDEX_PASSWORD GH_TOKEN VERSION
endif

VENV_DIR        := .venv
ENV_SCRIPT      := activate_env.sh

PROJECT_NAME    := $(notdir $(CURDIR))
CONTAINER_NAME  := $(shell echo "$(PROJECT_NAME)" | tr '[:upper:]' '[:lower:]' | tr -s ' _-' '-' | sed 's/-*$$//; s/^-*//')
REPO_URL        := $(shell git remote get-url origin 2>/dev/null)
REGISTRY_URL    := $(shell echo "$(REPO_URL)" | \
                     sed -e 's|https://gitlab\.com/|https://hub.docker.com//|' \
                         -e 's|\.git$$||' | tr '[:upper:]' '[:lower:]')
REGISTRY_PATH   := $(shell echo "$(REGISTRY_URL)" | sed 's|https://||')

ifeq ($(strip $(VERSION)),)
VERSION     := v$(shell grep '^version[[:space:]]*=' pyproject.toml | head -n 1 | sed 's/version[[:space:]]*=[[:space:]]*"\(.*\)"/\1/')
endif


# ──────────────────────────────────────────────────────────────────────────────
#  include files
# ──────────────────────────────────────────────────────────────────────────────
include make/build.mk
include make/clean.mk
include make/docker.mk
include make/docker-compose.mk
include make/docs.mk
include make/profiling.mk
include make/qa.mk
include make/run.mk
include make/settings.mk
include make/uv.mk



# ────────────────────────────────────────────────────────────────────────────
# CI CD METHODOLOGY
# ────────────────────────────────────────────────────────────────────────────

.PHONY: pr-review
pr-review: ## Prepare and run CI locally
	@echo "$(ARROW) Preparing PR review..." && git pull
	@test -f .env && cp .env .env.backup && echo "Backup created" || echo "No .env to backup"
	@echo -n "Overwrite .env with .env.example? [y/N] " && read ans && [ "$$ans" = "y" ] || (echo "Aborted"; exit 1)
	@cp .env.example .env && $(MAKE) ci
