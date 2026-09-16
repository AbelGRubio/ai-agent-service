# ─────────────────────────────────────────────────────────────────────────────
# Documentation
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: docs
docs: 	## Serve documentation locally
	@echo "$(ARROW) Serving documentation (mkdocs)..."
	@uv run mkdocs serve --livereload

.PHONY: docs-build
docs-build: ## Build documentation site
	@echo "$(ARROW) Building documentation site..."
	@uv run mkdocs build
	@echo "Documentation built $(OK)"
