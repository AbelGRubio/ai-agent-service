
# ─────────────────────────────────────────────────────────────────────────────
# Development / Run
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: run
run: sync ## Run MCP server
	@echo "$(ARROW) Starting server..."
	@uv run app.py


# ────────────────────────────────────────────────────────────────────────────
# RUN UVICORN
# ────────────────────────────────────────────────────────────────────────────
.PHONY: uvicorn
uvicorn: ## Run uvicorn
	@echo "$(ARROW) Launching uvicorn..."
	@PYTHONPATH=src uv run uvicorn src.__main__:app --host 0.0.0.0 --port 8000
	@echo "Ended uvicorn"

# ────────────────────────────────────────────────────────────────────────────
# RUN CONTAINER
# ────────────────────────────────────────────────────────────────────────────
.PHONY: run-container
run-container: docker-run ## Run MCP server in Docker
