"""Application factory for the Observe Me FastAPI server.

This module builds and configures the API application instance,
including routing, optional authentication middleware, CORS, and
Prometheus metrics instrumentation.
"""

import json
import os

# from observe_agent.router import router_agent
# from prometheus_fastapi_instrumentator import Instrumentator
import sys
from functools import lru_cache

from fastapi.middleware.cors import CORSMiddleware

# from observe_core import SessionMiddleware
from observe_core.logger import get_logger
from starlette.applications import Starlette

sys.path.insert(0, os.path.abspath("src"))
from langgraph_api.server import app as langgraph_app

logger = get_logger(__name__)


def load_config() -> dict:
    """Load the LangGraph configuration file and register graph definitions.

    Returns:
        dict: Parsed graph definitions loaded from `langgraph.json`.
    """
    graphs = {}
    try:
        with open("langgraph.json", encoding="utf-8") as f:
            config_data = json.load(f)

        graphs = config_data.get("graphs", {})
        os.environ["LANGSERVE_GRAPHS"] = json.dumps(graphs)

        logger.info(f"Graph file loaded: {graphs}")
    except FileNotFoundError as e:
        logger.error(f"No se pudo cargar el archivo langgraph.json en la raíz: {e}")
    return graphs


@lru_cache(maxsize=1)
def define_app(add_auth: bool = False) -> Starlette:
    """Create and configure the FastAPI application instance.

    Args:
        add_auth: Whether to attach the authentication middleware.

    Returns:
        A configured FastAPI application.

    """
    load_config()

    # langgraph_app.add_middleware(SessionMiddleware)

    # if add_auth:
    #     langgraph_app.add_middleware(AuthMiddleware)

    langgraph_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Instrumentator().instrument(app).expose(app)

    logger.info("Define fastapi server.")
    return langgraph_app
