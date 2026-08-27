"""Setup MCP node and bridge tools.

========================================================================================================================
Name:         apps/agent/src/observe_agent/nodes/setup_mcp_node.py
Description:  Build MCP resource-based tools and normalize MCP connection
              configuration for the agent runtime.
Project:      Observe me
Date:         2026-06-19 00:00:00
Status:       Development

Copyright ©2026. All rights reserved.
========================================================================================================================
"""

import asyncio
import copy
from collections.abc import Callable
from typing import Any

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_mcp_adapters.resources import load_mcp_resources
from observe_core.logger import get_logger

from observe_agent.jwt_utils import get_jwt_token
from observe_agent.mcp_types import MCPConfig
from observe_agent.nodes.state import AgentState, ConnectionConfig
from observe_agent.settings import default__mcp_config, get_settings

logger = get_logger(__name__)


async def create_mcp_bridge_tools(session: Any) -> list[Callable[..., Any]]:
    """Create tool wrappers for MCP resources exposed by a session.

    Args:
        session: MCP session object exposing resource access methods such as
            `read_resource` or `get_prompt`.

    Returns:
        A list of callables decorated as tools that can be injected into the
        agent's toolset.
    """
    resources_tools = await load_mcp_resources(session)

    mcp_resource_tools: list[Callable[..., Any]] = []
    for resource in resources_tools:
        uri_str = str(resource.metadata.get("uri"))
        resource_name = uri_str.rstrip("/").split("/")[-1]

        @tool(name_or_callable=f"read_{resource_name}")
        async def resource_tool(uri: str = uri_str) -> str:
            """Read the content of a specific MCP resource.

            The implementation uses the provided `session` to read the
            resource. The returned value is coerced to `str` to ensure the
            tool returns a JSON-serializable scalar.
            """
            content = await session.read_resource(uri)
            return str(content)

        mcp_resource_tools.append(resource_tool)  # type: ignore[bad-assignment]

    return mcp_resource_tools


async def setup_mcp_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """Normalize MCP config and optionally attach authentication tokens.

    Args:
        state: `AgentState` containing any pre-supplied `mcp_config` or
            `openai_api_key` values.
        config: RunnableConfig provided by the runtime (unused directly).

    Returns:
        Mapping to merge into graph state, typically `mcp_config` and
        `openai_api_key`.
    """
    logger.info("Configurando MCP y herramientas...")
    settings = get_settings()
    default_mcp_config = default__mcp_config(settings)

    mcp_config: MCPConfig = copy.deepcopy(state.get("mcp_config") or default_mcp_config)

    token: str = ""
    if settings.jwt_protected:
        logger.info("Retrieving token...")
        token = await asyncio.to_thread(get_jwt_token)  # type: ignore[bad-assignment]

    for name, raw_conn in mcp_config.items():
        logger.info(f"Parsing information server: '{name}'")
        validated_conn = ConnectionConfig(**raw_conn)  # type: ignore[bad-argument-type]
        if settings.jwt_protected:
            validated_conn.add_token(token)
        conn = validated_conn.model_dump()
        mcp_config[name] = conn  # type: ignore[unsupported-operation]

    openai_api_key = state.get("openai_api_key")
    state["openai_api_key"] = openai_api_key
    state["mcp_config"] = mcp_config

    return state
