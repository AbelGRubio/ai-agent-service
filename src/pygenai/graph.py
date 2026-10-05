"""Main entry point for the CopilotKit agent graph."""

from langchain_litellm import ChatLiteLLM
from langgraph.graph import StateGraph
from pygenai.rag.retriever import Retriever

from pygenai.logger import get_logger
from pygenai.nodes.chat_node import agent_node
from pygenai.nodes.setup_mcp_node import setup_mcp_node
from pygenai.nodes.state import AgentState
from pygenai.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()

workflow = StateGraph(state_schema=AgentState)

mi_retriever = Retriever()
llm = ChatLiteLLM(
    model="gpt-4o-mini",
    temperature=0,
    api_key=settings.llm_api_key.get_secret_value(),
    api_base=settings.model_base_url
)


# nodo_rag_con_retriever = partial(rag_node, retriever=mi_retriever, llm=llm)

workflow.add_node("setup", setup_mcp_node)  # type: ignore[no-matching-overload]
# workflow.add_node("retrieve", nodo_rag_con_retriever)
workflow.add_node("agent", agent_node)  # type: ignore[no-matching-overload]

workflow.set_entry_point("setup")
# workflow.add_edge("setup", "retrieve")
# workflow.add_edge("retrieve", "agent")
workflow.add_edge("setup", "agent")

# Compile the workflow graph
graph = workflow.compile()  # MemorySaver()
