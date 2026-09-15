"""Main entry point for the CopilotKit agent graph."""

from langgraph.graph import StateGraph
from observe_core.logger import get_logger

from observe_agent.nodes.chat_node import agent_node
from observe_agent.nodes.rag_node import rag_node
from observe_agent.nodes.setup_mcp_node import setup_mcp_node
from observe_agent.nodes.state import AgentState

logger = get_logger(__name__)

workflow = StateGraph(state_schema=AgentState)

workflow.add_node("setup", setup_mcp_node)
workflow.add_node("retrieve", rag_node)
workflow.add_node("agent", agent_node)

workflow.set_entry_point("setup")
workflow.add_edge("setup", "retrieve")
workflow.add_edge("retrieve", "agent")

# Compile the workflow graph
graph = workflow.compile()  # MemorySaver()
