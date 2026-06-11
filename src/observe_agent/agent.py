"""Main entry point for the CopilotKit agent graph."""

import copy
from contextlib import AsyncExitStack
from typing import Literal

import httpx
from copilotkit import CopilotKitState
from copilotkit.langgraph import copilotkit_exit
from langchain.agents import create_agent
from langchain_core.runnables import RunnableConfig
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.types import Command
from observe_core.logger_api import get_logger
from pydantic import BaseModel, Field

from observe_agent.mcp_types import MCPConfig
from observe_agent.settings import default__mcp_config, get_settings

logger = get_logger(__name__)


class ConnectionConfig(BaseModel):
    """Normalized MCP connection payload."""

    url: str
    headers: dict[str, str] = Field(default_factory=dict)
    transport: str = Field(default="http")


class AgentState(CopilotKitState):
    """Agent state passed across the langgraph workflow.

    In this instance, we're inheriting from CopilotKitState, which will bring in
    the CopilotKitState fields. We're also adding a custom field, `mcp_config`,
    which will be used to configure MCP services for the agent.
    """

    # Define mcp_config as an optional field without skipping validation
    mcp_config: MCPConfig | None
    openai_api_key: str | None


def get_jwt_token() -> str:
    """Retrieve a JWT token for outbound MCP calls."""
    settings = get_settings()
    if not settings.client_id or not settings.client_secret:
        raise ValueError("CLIENT_ID and CLIENT_SECRET are required when JWT protection is enabled")

    response = httpx.post(
        settings.jwt_url,
        data={"grant_type": "client_credentials"},
        auth=(settings.client_id, settings.client_secret),
        timeout=10.0,
    )
    response.raise_for_status()
    payload = response.json()
    token = payload.get("access_token")
    if not token:
        raise ValueError("JWT response does not include access_token")
    return token


# Default MCP configuration to use when no configuration is provided in the state
# Uses relative paths that will work within the project structure


async def chat_node(state: AgentState, config: RunnableConfig) -> Command[Literal["__end__"]]:
    """Run the chat agent and loaded MCP tools.

    This is a simplified agent that uses the ReAct agent as a subgraph.
    It handles both chat responses and tool execution in one node.
    """
    logger.info("Starting chat_node execution...")

    settings = get_settings()
    default_mcp_config = default__mcp_config(settings)

    mcp_config: MCPConfig = copy.deepcopy(state.get("mcp_config") or default_mcp_config)
    logger.info(f"Using MCP configuration: {mcp_config}")

    # Validate all connections and process their headers (e.g. inject JWT tokens if HTTP)
    for name, raw_conn in mcp_config.items():
        validated_conn = ConnectionConfig(**raw_conn)
        conn = validated_conn.model_dump()
        mcp_config[name] = conn

        logger.info(f"Configuring MCP '{name}' with URL: {conn.get('url')} and transport: {conn.get('transport')}")

        # Only HTTP transport supports headers
        if conn.get("transport") == "http":
            if "headers" not in conn:
                default_conn = default_mcp_config.get(name) or default_mcp_config[next(iter(default_mcp_config))]
                conn["headers"] = copy.copy(default_conn.get("headers", {}))

            headers = conn["headers"]

            # Manage Authorization Header for HTTP endpoints
            if settings.jwt_protected:
                logger.info(f"[{name}] JWT_PROTECTED is enabled. Retrieving token...")
                headers["Authorization"] = f"Bearer {get_jwt_token()}"
            else:
                headers.pop("Authorization", None)

    # Get OpenAI API key from state
    openai_api_key = state.get("openai_api_key")

    # Set up the multi-server MCP client using the full configuration
    mcp_client = MultiServerMCPClient(mcp_config)

    # Dynamically connect to ALL configured MCP servers and load their tools using an AsyncExitStack
    mcp_tools = []

    async with AsyncExitStack() as stack:
        for name in mcp_config:
            logger.info(f"Connecting to session for MCP server: '{name}'")
            session = await stack.enter_async_context(mcp_client.session(name))
            server_tools = await load_mcp_tools(session)
            mcp_tools.extend(server_tools)

        logger.info(f"Successfully loaded a total of {len(mcp_tools)} tools from all MCP servers.")

        # Create the react agent with ALL consolidated tools
        model = ChatOpenAI(model=settings.model_name, api_key=openai_api_key)
        react_agent = create_agent(model, mcp_tools)

        # Prepare messages for the react agent
        agent_input = {"messages": state["messages"]}

        # Run the react agent subgraph with our input
        agent_response = await react_agent.ainvoke(agent_input)

    # Update the state with the new messages
    updated_messages = state["messages"] + agent_response.get("messages", [])
    await copilotkit_exit(config)
    # End the graph with the updated messages
    # added the openai_api_keyand the mcp_config to modify the state
    return Command(
        goto=END,
        update={
            "messages": updated_messages,
            "openai_api_key": state.get("openai_api_key"),
            "mcp_config": state.get("mcp_config", default_mcp_config),
        },
    )


# Define the workflow graph with only a chat node
workflow = StateGraph(AgentState)
workflow.add_node("chat_node", chat_node)
workflow.set_entry_point("chat_node")

# Compile the workflow graph
graph = workflow.compile()  # MemorySaver()
