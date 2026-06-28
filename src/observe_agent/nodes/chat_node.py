"""Main entry point for the CopilotKit agent graph.

========================================================================================================================
Name:         apps/agent/src/observe_agent/nodes/chat_node.py
Description:  Entrypoint node that runs the copilot/agent using configured MCP tools and an LLM model.
Project:      Observe me
Date:         2026-06-19 00:00:00
Status:       Development

Copyright ©2026. All rights reserved.
========================================================================================================================
"""

import copy
from contextlib import AsyncExitStack

from copilotkit.langgraph import copilotkit_exit
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI

# from langchain_openai import ChatOpenAI
from langgraph.graph import END
from langgraph.types import Command
from observe_core.logger import get_logger

from observe_agent.mcp_manager import get_mcp_manager
from observe_agent.mcp_types import MCPConfig
from observe_agent.nodes.state import AgentState
from observe_agent.settings import default__mcp_config, get_settings

logger = get_logger(__name__)
manager = get_mcp_manager()


async def agent_node(state: AgentState, config: RunnableConfig) -> Command:
    """Run the Copilot/agent node.

    Connects to configured MCP servers, loads available MCP tools, instantiates
    an LLM-backed agent, invokes it with the current conversation messages,
    and returns a `Command` instructing the graph to continue.

    Args:
        state: `AgentState` holding runtime keys such as `messages`, optional
            `mcp_config`, and `rag_context` used to enrich system prompts.
        config: `RunnableConfig` provided by the runtime; used to perform a
            graceful exit via `copilotkit_exit` when the agent finishes.

    Returns:
        `Command`: A `langgraph.types.Command` with `goto` and `update` fields
        to drive the graph and update the shared state (e.g., `messages`).

    Raises:
        Exception: Any error raised during agent invocation is logged and
        re-raised to surface failures to the caller.
    """
    logger.info("Ejecutando el agente...")
    # Load application settings and compute the default MCP configuration
    settings = get_settings()
    default_mcp_config = default__mcp_config(settings)
    # Prefer MCP configuration supplied in state; fall back to project defaults
    mcp_config: MCPConfig = copy.deepcopy(state.get("mcp_config") or default_mcp_config)

    # Multi-server MCP client will manage sessions to one or more MCP servers
    mcp_client = MultiServerMCPClient(mcp_config)  # type: ignore[bad-argument-type]
    mcp_tools = []

    # Use an AsyncExitStack so all MCP sessions are closed on exit
    async with AsyncExitStack() as stack:
        for name in mcp_config:
            logger.info(f"Connecting to session for MCP server: '{name}'")
            # Open a session for each configured MCP server and load its tools
            session = await stack.enter_async_context(mcp_client.session(name))
            server_tools = await load_mcp_tools(session)
            mcp_tools.extend(server_tools)

        # Instantiate the LLM client with the configured model and API key
        model = ChatOpenAI(
            model="gpt-4o",
            api_key=settings.openai_api_key.get_secret_value(),
            base_url=settings.model_base_url,
        )
        # Inject RAG (retrieval) context into the system prompt if present.
        # NOTE: integration into the actual message list may be required upstream.
        # system_prompt = f"Contexto disponible: {state.get('rag_context')}"

        if not mcp_tools:
            logger.warning("No se encontraron herramientas MCP cargadas en el estado.")

        # Create a react-style agent wired to the LLM and the loaded tools
        react_agent = create_agent(model, mcp_tools)

        try:
            rag_context = state.get("rag_context", [])

            # 2. Prepare the augmented messages list
            # We create a new list so we don't mutate the original state["messages"] permanently
            messages = list(state["messages"])

            if rag_context:
                # Join documents into a clean string
                context_text = "\n\n".join(rag_context)

                # Create the context message
                context_message = SystemMessage(
                    content=f"Utiliza el siguiente contexto proporcionado para responder a la"
                    f" pregunta del usuario:\n\n{context_text}"
                )

                # Prepend it to the list (or insert it after the very first system prompt if you have one)
                messages.insert(0, context_message)

            # Invoke the agent asynchronously with the current conversation messages
            agent_response = await react_agent.ainvoke({"messages": messages})
            # Merge incoming messages from the agent with the existing conversation
            updated_messages = state["messages"] + agent_response.get("messages", [])

            # Ensure any runtime cleanup / graceful exit is performed
            await copilotkit_exit(config)

            return Command(
                goto=END,
                update={"messages": updated_messages},
            )
        except Exception as e:
            # Log the error for observability, then re-raise to surface failure
            logger.error(f"Error durante la ejecución del agente: {e}")
            raise e
