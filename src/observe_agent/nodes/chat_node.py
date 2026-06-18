"""Main entry point for the CopilotKit agent graph."""
import copy
from contextlib import AsyncExitStack

from copilotkit.langgraph import copilotkit_exit
from langchain.agents import create_agent
from langchain_core.runnables import RunnableConfig
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from langgraph.graph import END
from langgraph.types import Command
from observe_core.logger_api import get_logger

from observe_agent.mcp_types import MCPConfig
from observe_agent.nodes.state import AgentState
from observe_agent.settings import default__mcp_config, get_settings
from observe_agent.mcp_manager import get_mcp_manager

logger = get_logger(__name__)
manager = get_mcp_manager()

async def agent_node(state: AgentState, config: RunnableConfig):
    logger.info("Ejecutando el agente...")
    settings = get_settings()
    default_mcp_config = default__mcp_config(settings)
    mcp_config: MCPConfig = copy.deepcopy(state.get("mcp_config") or default_mcp_config)

    mcp_client = MultiServerMCPClient(mcp_config)
    mcp_tools = []

    async with AsyncExitStack() as stack:

        for name in mcp_config:
            logger.info(f"Connecting to session for MCP server: '{name}'")
            session = await stack.enter_async_context(mcp_client.session(name))
            server_tools = await load_mcp_tools(session)
            mcp_tools.extend(server_tools)

        model = ChatOpenAI(model=settings.model_name, api_key=settings.openai_api_key.get_secret_value())
        # Inyectamos el contexto de RAG en el prompt del sistema
        system_prompt = f"Contexto disponible: {state.get('rag_context')}"

        if not mcp_tools:
            logger.warning("No se encontraron herramientas MCP cargadas en el estado.")

        react_agent = create_agent(model, mcp_tools)

        try:
            # Ejecutamos
            agent_response = await react_agent.ainvoke({"messages": state["messages"]})
            updated_messages = state["messages"] + agent_response.get("messages", [])

            await copilotkit_exit(config)

            return Command(
                goto=END,
                update={"messages": updated_messages},
            )
        except Exception as e:
            logger.error(f"Error durante la ejecución del agente: {e}")
            raise e