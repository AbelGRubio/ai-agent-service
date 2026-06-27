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

import asyncio

from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from observe_core.logger import get_logger

from observe_agent.nodes.state import AgentState
from observe_agent.rag.retriever import Retriever

logger = get_logger(__name__)


async def rag_node(state: AgentState, retriever: Retriever, llm: ChatOpenAI) -> dict[str, object]:
    """Retrieve relevant documents and return updated RAG context.

    This node performs retrieval using the provided `Retriever` instance and
    stores a lightweight representation of retrieved content under the
    `rag_context` key returned to the graph state.

    Args:
        state: Current `AgentState` (graph-local state object).
        retriever: Retriever instance capable of fetching documents for a
            given query.
        llm: Chat OpenAI

    Returns:
        A dict containing keys to merge into the graph state. Example:
        `{"rag_context": <str or list>}`.

    Raises:
        ValueError: If the retrieval operation fails for any reason.
    """
    logger.info("Analizando necesidad de RAG...")

    # 1. Obtener el último mensaje del humano
    # Buscamos en orden inverso para encontrar el más reciente
    last_human_message = next((m for m in reversed(state["messages"]) if isinstance(m, HumanMessage)), None)
    user_query = last_human_message.content if last_human_message else ""
    logger.info(f"La query es: {user_query}")

    # 2. Definir prompt de reformulación
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Eres un experto en decidir si una consulta requiere buscar en documentos internos de la empresa. "
            "Tu objetivo es transformar la pregunta del usuario en una consulta de búsqueda eficiente"
            " para un sistema RAG. "
            "\n\nREGLAS:"
            "1. Si la pregunta requiere conocer documentos internos, políticas, manuales o datos específicos "
            "de la empresa, devuelve la consulta de búsqueda optimizada."
            "2. Si la pregunta es casual, de saludo o general (ej. 'hola', 'qué tal'), responde 'NO_RAG'."
            "\n\nEJEMPLOS:"
            "Usuario: ¿Cuál es la política de empresa? -> Consulta: política interna de la empresa documento oficial"
            "Usuario: Hola, ¿cómo estás? -> NO_RAG"
            "Usuario: ¿Cómo pido vacaciones? -> Consulta: proceso solicitud vacaciones política empresa"
            "\n\nSi no estás seguro, asume que se necesita RAG para asegurar la veracidad.",
        ),
        ("user", "{question}"),
    ])

    chain = prompt | llm
    reformulated_query = await chain.ainvoke({"question": user_query})

    # 3. Llamada al LLM para reformular
    # reformulated_query = await chain.ainvoke({"question": user_query})
    query_text = reformulated_query.content.strip()
    logger.info(reformulated_query)
    if query_text == "NO_RAG":
        logger.info("El LLM determinó que no se necesita RAG.")
        return {"rag_context": []}

    try:
        logger.info(f"Pregunta detectada: {query_text}. Ejecutando búsqueda...")
        # `retriever.invoke` may be synchronous or asynchronous depending on
        # implementation. This code preserves the existing call-site semantics.
        docs = await asyncio.to_thread(retriever.invoke, query_text)
        documents = [doc.page_content for doc in docs]
        # Normalize retrieved documents into a minimal payload for the agent
        state["rag_context"] = documents
        logger.debug(f"Retrieved {len(docs)} documents for query: {query_text}")
    except Exception as e:
        logger.error(f"Failed to retrieve documents: {e}")
        documents = []
        raise ValueError(f"Failed to retrieve documents: {e}") from e

    return {"rag_context": documents}
