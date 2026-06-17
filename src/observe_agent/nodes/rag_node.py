
from observe_core.logger_api import get_logger
from .state import AgentState

logger = get_logger(__name__)


async def rag_node(state: AgentState) -> dict:
    logger.info("Ejecutando lógica de RAG...")
    # Aquí usarías las herramientas cargadas o lógica propia para buscar info
    # Ejemplo:
    context = "Información extraída de los recursos MCP..."
    return {"rag_context": context}
