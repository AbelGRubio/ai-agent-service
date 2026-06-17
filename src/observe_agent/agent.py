"""Main entry point for the CopilotKit agent graph."""

# import copy
# from contextlib import AsyncExitStack
# from typing import Literal
#
# import asyncio
#
#
# from copilotkit.langgraph import copilotkit_exit
# from langchain.agents import create_agent
# from langchain_core.runnables import RunnableConfig
# from langchain_mcp_adapters.client import MultiServerMCPClient
# from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
# from langgraph.types import Command
from observe_core.logger_api import get_logger

from observe_agent.nodes.state import AgentState
from observe_agent.nodes.rag_node import rag_node
from observe_agent.nodes.chat_node import agent_node
from observe_agent.nodes.setup_mcp_node import setup_mcp_node
# from observe_agent.nodes.setup_mcp_node import create_mcp_bridge_tools
# from observe_agent.nodes.setup_mcp_node import load_mcp_tools
# from observe_agent.mcp_types import MCPConfig
# from observe_agent.settings import default__mcp_config, get_settings
# from observe_agent.jwt_utils import get_jwt_token


logger = get_logger(__name__)

# Default MCP configuration to use when no configuration is provided in the state
# Uses relative paths that will work within the project structure


# async def chat_node(state: AgentState, config: RunnableConfig) -> Command[Literal["__end__"]]:
#     """Run the chat agent and loaded MCP tools.
#
#     This is a simplified agent that uses the ReAct agent as a subgraph.
#     It handles both chat responses and tool execution in one node.
#     """
#     logger.info("Starting chat_node execution...")
#
#     settings = get_settings()
#     default_mcp_config = default__mcp_config(settings)
#
#     mcp_config: MCPConfig = copy.deepcopy(state.get("mcp_config") or default_mcp_config)
#     logger.info(f"Using MCP configuration: {mcp_config}")
#
#     # Validate all connections and process their headers (e.g. inject JWT tokens if HTTP)
#     for name, raw_conn in mcp_config.items():
#         validated_conn = ConnectionConfig(**raw_conn)
#         conn = validated_conn.model_dump()
#         mcp_config[name] = conn
#
#         logger.info(f"Configuring MCP '{name}' with URL: {conn.get('url')} and transport: {conn.get('transport')}")
#
#         # Only HTTP transport supports headers
#         if conn.get("transport") == "http":
#             if "headers" not in conn:
#                 default_conn = default_mcp_config.get(name) or default_mcp_config[next(iter(default_mcp_config))]
#                 conn["headers"] = copy.copy(default_conn.get("headers", {}))
#
#             headers = conn["headers"]
#
#             # Manage Authorization Header for HTTP endpoints
#             if settings.jwt_protected:
#                 logger.info(f"[{name}] JWT_PROTECTED is enabled. Retrieving token...")
#                 token = await asyncio.to_thread(get_jwt_token)
#                 headers["Authorization"] = f"Bearer {token}"
#             else:
#                 headers.pop("Authorization", None)
#
#     # Get OpenAI API key from state
#     openai_api_key = state.get("openai_api_key")
#
#     # Set up the multi-server MCP client using the full configuration
#     mcp_client = MultiServerMCPClient(mcp_config)
#
#     # Dynamically connect to ALL configured MCP servers and load their tools using an AsyncExitStack
#     mcp_tools = []
#
#     async with AsyncExitStack() as stack:
#         for name in mcp_config:
#             logger.info(f"Connecting to session for MCP server: '{name}'")
#             session = await stack.enter_async_context(mcp_client.session(name))
#             server_tools = await load_mcp_tools(session)
#             mcp_tools.extend(server_tools)
#             resources_tools = await create_mcp_bridge_tools(session)
#             mcp_tools.extend(resources_tools)
#
#         logger.info(f"Successfully loaded a total of {len(mcp_tools)} tools from all MCP servers.")
#
#         # Create the react agent with ALL consolidated tools
#         model = ChatOpenAI(model=settings.model_name, api_key=openai_api_key)
#         react_agent = create_agent(model, mcp_tools)
#
#         # Prepare messages for the react agent
#         agent_input = {"messages": state["messages"]}
#
#         # Run the react agent subgraph with our input
#         agent_response = await react_agent.ainvoke(agent_input)
#
#     # Update the state with the new messages
#     updated_messages = state["messages"] + agent_response.get("messages", [])
#     await copilotkit_exit(config)
#     # End the graph with the updated messages
#     # added the openai_api_keyand the mcp_config to modify the state
#     return Command(
#         goto=END,
#         update={
#             "messages": updated_messages,
#             "openai_api_key": state.get("openai_api_key"),
#             "mcp_config": state.get("mcp_config", default_mcp_config),
#         },
#     )


# Define the workflow graph with only a chat node
workflow = StateGraph(AgentState)
# workflow.add_node("chat_node", chat_node)
# workflow.set_entry_point("chat_node")

workflow.add_node("setup", setup_mcp_node)
workflow.add_node("retrieve", rag_node)
workflow.add_node("agent", agent_node)

workflow.set_entry_point("setup")
workflow.add_edge("setup", "retrieve")
workflow.add_edge("retrieve", "agent")

# Compile the workflow graph
graph = workflow.compile()  # MemorySaver()
