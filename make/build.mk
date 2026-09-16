
# ─────────────────────────────────────────────────────────────────────────────
# Build & Publish
# ─────────────────────────────────────────────────────────────────────────────
.PHONY: build
build: 	## Build package(s)
	@echo "$(ARROW) Building package(s)..."
	@uv build --all-packages || { echo "❌ Build failed."; exit 1; }
	@echo "Build completed $(OK)"

.PHONY: artifact
artifact: build

.PHONY: publish
publish: check-venv	## Publish new version using semantic-release
	@echo "$(ARROW) Publishing release..."
	@GH_TOKEN=$(GH_TOKEN) uv run semantic-release publish || { echo "$(FAIL) Publish failed"; exit 1; }
	@echo "$(OK) Release published"

.PHONY: semantic-release
semantic-release: ## Execute semantic-release to get new version
	@echo "$(ARROW) Running semantic-release version..."
	@GH_TOKEN=$(GH_TOKEN) uv run semantic-release -vv version
	@echo "$(OK) Semantic release version check completed"
