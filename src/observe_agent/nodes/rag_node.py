"""RAG node: retrieves documents to enrich agent context.

========================================================================================================================
Name:         apps/agent/src/observe_agent/nodes/rag_node.py
Description:  Node responsible for retrieval-augmented generation (RAG).
Project:      Observe me
Date:         2026-06-19 00:00:00
Status:       Development

Copyright ©2026. All rights reserved.
========================================================================================================================
"""

from observe_core.logger import get_logger

from observe_agent.nodes.state import AgentState
from observe_agent.rag.retriever import Retriever

logger = get_logger(__name__)


def rag_node(state: AgentState, retriever: Retriever) -> dict[str, object]:
    """Retrieve relevant documents and return updated RAG context.

    This node performs retrieval using the provided `Retriever` instance and
    stores a lightweight representation of retrieved content under the
    `rag_context` key returned to the graph state.

    Args:
        state: Current `AgentState` (graph-local state object).
        retriever: Retriever instance capable of fetching documents for a
            given query.

    Returns:
        A dict containing keys to merge into the graph state. Example:
        `{"rag_context": <str or list>}`.

    Raises:
        ValueError: If the retrieval operation fails for any reason.
    """
    logger.info("Ejecutando lógica de RAG...")
    # Example retrieval flow; real implementations will reformulate user
    # queries, call the retriever, and normalize documents into the state.
    context = "Información extraída de los recursos MCP..."

    try:
        reformulated_question = context
        # `retriever.invoke` may be synchronous or asynchronous depending on
        # implementation. This code preserves the existing call-site semantics.
        docs = retriever.invoke(reformulated_question)
        # Normalize retrieved documents into a minimal payload for the agent
        state.rag_context = [doc.page_content for doc in docs]
        logger.debug(f"Retrieved {len(docs)} documents for query: {reformulated_question}")
    except Exception as e:
        logger.error(f"Failed to retrieve documents: {e}")
        raise ValueError(f"Failed to retrieve documents: {e}") from e

    return {"rag_context": context}
