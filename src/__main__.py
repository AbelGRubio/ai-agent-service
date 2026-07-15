"""Entry point."""

import uvicorn
from observe_agent.app import define_app
from observe_core.logger import get_logger, propague_loggers


logger = get_logger(__name__)

app = define_app()

propague_loggers()


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
