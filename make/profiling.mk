# ──────────────────────────────────────────────────────────────────────────────
#  Profiling
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: profile profile-memory
profile: ## Make a profice from src
	@echo off & set RABBITMQ_USER=guest & set RABBITMQ_PSSWRD=guest & set DISABLE_SYSLOG=true & \
	uv run python -m cProfile -o profiler_worker.profile src/__main__.py & \
	uv run snakeviz profiler_worker.profile

profile-memory: ## Make a profile memory
	@echo off & set RABBITMQ_USER=guest & set RABBITMQ_PSSWRD=guest & set DISABLE_SYSLOG=true & \
	uv run mprof run --multiprocess src/__main__.py; \
	uv run mprof plot --title "Profiler Real Observability"
