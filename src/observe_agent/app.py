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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from observe_core import SessionMiddleware
from observe_core.logger_api import get_logger

sys.path.insert(0, os.path.abspath("src"))
from langgraph_api.server import app as langgraph_app
from langgraph_runtime.lifespan import lifespan

logger = get_logger(__name__)


def load_config() -> dict:
    """Create and configure the FastAPI application instance.

    Returns:
    """
    graphs = {}
    try:
        with open("langgraph.json", encoding="utf-8") as f:
            config_data = json.load(f)

        graphs = config_data.get("graphs", {})
        os.environ["LANGSERVE_GRAPHS"] = json.dumps(graphs)

        logger.info(f"Configuración de grafos cargada globalmente: {graphs}")
    except FileNotFoundError as e:
        logger.error(f"No se pudo cargar el archivo langgraph.json en la raíz: {e}")
    return graphs


@lru_cache(maxsize=1)
def define_app(add_auth: bool = False) -> FastAPI:
    """Create and configure the FastAPI application instance.

    Args:
        add_auth: Whether to attach the authentication middleware.

    Returns:
        A configured FastAPI application.

    """
    load_config()
    # langgraph_config = Config(graphs=load_config())
    app = FastAPI(title="Observer agent", summary="Observer agent", version="0.1.0", lifespan=lifespan)

    app.add_middleware(SessionMiddleware)

    # if add_auth:
    #     app.add_middleware(AuthMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/", langgraph_app)
    # app.include_router(router=router_agent)

    # Instrumentator().instrument(app).expose(app)

    logger.info("Define fastapi server.")
    return app
