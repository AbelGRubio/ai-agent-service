
ifeq ($(strip $(VERSION)),)
VERSION     := v$(shell grep '^version[[:space:]]*=' pyproject.toml | head -n 1 | sed 's/version[[:space:]]*=[[:space:]]*"\(.*\)"/\1/')
endif

# Línea de referencia en pyproject.toml
UV_FILE=pyproject.toml


.PHONY: uv-docker
uv-docker: ## Change index for observe-core for second context in dockerfile.
	@echo "Configurando observe-core para DOCKER (editable=false)..."
	@sed 's|observe-core = .*|observe-core = { path = "../observe_core", editable = false }|' $(UV_FILE) > $(UV_FILE).tmp && mv $(UV_FILE).tmp $(UV_FILE)

.PHONY: uv-local
uv-local: ## Change index for observe-core for second context in dockerfile.
	@echo "Configurando observe-core para DOCKER (editable=false)..."
	@sed 's|observe-core = .*|observe-core = { path = "../../libs/observe_core", editable = false }|' $(UV_FILE) > $(UV_FILE).tmp && mv $(UV_FILE).tmp $(UV_FILE)


.PHONY: docker-build
docker-build: uv-docker ## Build Docker image
	@docker build --platform linux/amd64 -f Dockerfile \
		--build-context observe-core=../../libs/observe_core \
		-t observe_agent:$(VERSION) --no-cache --load . \
		&& echo "$(ARROW) Building image... done"
	@$(MAKE) uv-local


# ─────────────────────────────────────────────────────────────────────────────
# Testing
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: test
test: ## Run all tests
	@echo "$(ARROW) Running tests..."
	@uv run pytest -v --tb=short --disable-warnings --maxfail=1 || { echo "$(FAIL) Tests failed"; exit 1; }
	@echo "$(OK) All tests passed"
