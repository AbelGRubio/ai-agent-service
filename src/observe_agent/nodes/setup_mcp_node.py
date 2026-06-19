import asyncio
import copy

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_mcp_adapters.resources import load_mcp_resources
from observe_core.logger import get_logger

from observe_agent.jwt_utils import get_jwt_token
from observe_agent.mcp_types import MCPConfig
from observe_agent.settings import default__mcp_config, get_settings

from .state import AgentState, ConnectionConfig

logger = get_logger(__name__)


async def create_mcp_bridge_tools(session):
    resources_tools = await load_mcp_resources(session)

    mcp_resource_tools = []
    for resource in resources_tools:
        uri_str = str(resource.metadata.get("uri"))
        resource_name = uri_str.rstrip("/").split("/")[-1]

        @tool(name_or_callable=f"read_{resource_name}")
        async def resource_tool(uri: str = uri_str) -> str:
            """Lee el contenido de un recurso MCP específico."""
            content = await session.read_resource(uri)
            # El contenido suele venir en una lista de objetos,
            # nos aseguramos de devolver el texto plano
            return str(content)

        mcp_resource_tools.append(resource_tool)

    # @tool
    # async def get_mcp_prompt(prompt_name: str, arguments: dict = None) ->
    # str:
    #     """Obtiene y renderiza un prompt desde el servidor MCP."""
    #     result = await session.get_prompt(prompt_name, arguments=arguments)
    #     return str(result)

    return mcp_resource_tools


async def setup_mcp_node(state: AgentState, config: RunnableConfig) -> dict:
    logger.info("Configurando MCP y herramientas...")
    settings = get_settings()
    default_mcp_config = default__mcp_config(settings)

    mcp_config: MCPConfig = copy.deepcopy(state.get("mcp_config") or default_mcp_config)

    token: str = ""
    if settings.jwt_protected:
        logger.info("Retrieving token...")
        token: str = await asyncio.to_thread(get_jwt_token)

    for name, raw_conn in mcp_config.items():
        logger.info(f"Parsing information server: '{name}'")
        validated_conn = ConnectionConfig(**raw_conn)
        if settings.jwt_protected:
            validated_conn.add_token(token)
        conn = validated_conn.model_dump()
        mcp_config[name] = conn

    openai_api_key = state.get("openai_api_key")
    return {"mcp_config": mcp_config, "openai_api_key": openai_api_key}
