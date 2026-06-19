from observe_core.logger import get_logger

from observe_agent.nodes.state import AgentState
from observe_agent.rag.retriever import Retriever

logger = get_logger(__name__)


async def rag_node(state: AgentState, retriever: Retriever) -> dict:
    """Retrieve relevant documents if the intent is 'retrieve'.

    Args:
        state (GraphState): The current graph state.
        retriever (Retriever): The retriever instance to use for document retrieval.

    Returns:
        GraphState: Updated state with retrieved documents.

    Raises:
        ValueError: If document retrieval fails.
    """
    logger.info("Ejecutando lógica de RAG...")
    # Aquí usarías las herramientas cargadas o lógica propia para buscar info
    # Ejemplo:
    context = "Información extraída de los recursos MCP..."
    try:
        reformulated_question = context
        docs = retriever.invoke(reformulated_question)
        state.rag_context = [doc.page_content for doc in docs]
        logger.debug(f"Retrieved {len(docs)} documents for query: {reformulated_question}")
    except Exception as e:
        logger.error(f"Failed to retrieve documents: {e}")
        raise ValueError(f"Failed to retrieve documents: {e}") from e

    return {"rag_context": context}
