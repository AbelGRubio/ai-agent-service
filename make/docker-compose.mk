# ──────────────────────────────────────────────────────────────────────────────
#  Docker compose
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: compose-down compose-logs compose-up

compose-up: ## Execute docker-compose up in docker folder
	@cd infra && REGISTRY_PATH=$(REGISTRY_PATH) VERSION=$(VERSION) \
		docker-compose up -d

compose-down: ## Execute docker-compose down in docker folder
	@cd infra && docker-compose down

compose-logs: ## Execute docker-compose logs in docker folder
	@cd infra && REGISTRY_PATH=$(REGISTRY_PATH) VERSION=$(VERSION) \
		docker-compose logs -f observe_agent

.PHONY: compose-all
compose-all: compose-up compose-logs  ## Execute build, up and log.
