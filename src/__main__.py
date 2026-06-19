"""Entry point."""

import logging

import uvicorn
from observe_agent.app import define_app
from observe_core.logger import get_logger

logger = get_logger(__name__)

app = define_app()

# To put all loggers in same format.
for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
    uvicorn_logger = logging.getLogger(name)
    uvicorn_logger.handlers = logger.handlers
    uvicorn_logger.setLevel(logging.DEBUG)
    uvicorn_logger.propagate = False


if __name__ == "__main__":
    logger.debug("Starting...")
    uvicorn.run(
        app=app,
        host="10.0.0.2",
        port=8123,
        log_config=None,
        reload=False,
    )
    logger.debug("Ending.")
