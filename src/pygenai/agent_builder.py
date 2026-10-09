from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union
import uuid

from langchain.agents import create_agent
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_litellm import ChatLiteLLM
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import StreamableHttpConnection, StdioConnection, SSEConnection, \
    WebsocketConnection
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from typing_extensions import TypeAlias, TypedDict

from pygenai.core.base_memory import MemoryTypes
from pygenai.core.base_retriever import BaseRetriever
from pygenai.settings import get_settings
from pygenai.utils.mcp_manager import get_mcp_manager

MCPConnection: TypeAlias = Union[
    StdioConnection,
    SSEConnection,
    StreamableHttpConnection,
    WebsocketConnection
]


@dataclass
class LLMConfig:
    """Configuration class for LLM instances."""
    provider: str
    model_name: str
    api_base: Optional[str] = None
    temperature: float = 0.7
    timeout: Optional[float] = None
    retry_config: Dict[str, Any] = field(default_factory=lambda: {"max_retries": 2})


class AgentState(TypedDict):
    """Defines the expanded state structure for the LangGraph agent across modular nodes."""
    messages: list[BaseMessage]
    context: dict[str, Any]
    rag_query: Optional[str]
    rag_texts: list[str]
    tools: list[Any]
    memory_data: dict[str, Any]
    session_id: Optional[str]

class AgentBuilder:
    """Builder class for constructing LangGraph agents following SOLID principles.

    Allows fluent configuration of LLMs, RAG sources, memory systems, MCPs, and skills,
    utilizing a decoupled multi-node architecture for faster reasoning workflows.
    """

    def __init__(self, state_schema: Any = AgentState) -> None:
        """Initialize the AgentBuilder with empty configurations."""
        self._state_schema = state_schema
        self._rag_sources: Dict[str, BaseRetriever] = {}
        self._memory: Optional[MemoryTypes] = None
        self._skills: list[Any] = []
        self._mcps: list[MCPConnection] = []
        self._mcp_client: Optional[MultiServerMCPClient] = None
        self._mcp_manager = get_mcp_manager()
        self._define_default_llm()

    def _define_default_llm(self) -> None:
        """Define a default LLM configuration if none is provided."""
        settings = get_settings()

        self._llm = ChatLiteLLM(
            model="openai/gpt-4o-mini",
            temperature=0.7,
            api_key=settings.llm_api_key.get_secret_value(),
            api_base=settings.model_base_url
        )

    async def _start_mcp_client(self) -> None:
        """Initialize the MultiServerMCPClient if MCP configurations are provided."""
        if self._mcps and not self._mcp_client:
            self._mcp_client = MultiServerMCPClient(self._mcps)  # type: ignore[arg-type]

        await self._mcp_manager.get_active_tools(self._mcps, self._mcp_client)

    # --- Node 1: Prepara pregunta para RAG ---
    async def prepare_rag_query_node(self, state: AgentState, config: RunnableConfig) -> dict[str, Any]:
        """Extract the user's latest query and retrieve relevant context from RAG sources."""
        configurable = config.get("configurable", {})
        session_id = configurable.get("thread_id")
        if not session_id:
            session_id = str(uuid.uuid1())
        if not self._rag_sources:
            return {'session_id': session_id}

        messages: list[BaseMessage] = state.get("messages", [])
        if not messages:
            return {'session_id': session_id}

        last_msg = messages[-1]
        if isinstance(last_msg, HumanMessage):
            rag_query = last_msg.content
        elif isinstance(last_msg, dict):
            rag_query = last_msg.get('content', str(last_msg))
        else:
            rag_query = getattr(last_msg, "content", str(last_msg))

        rag_texts = []

        decision_prompt = (
            "Analyze if the following user query requires external knowledge retrieval "
            "from a document database to provide an accurate answer.\n"
            f"Original query: '{rag_query}'\n\n"
            "Formatting instructions:\n"
            "- If it requires external documents, respond strictly with 'YES: ' "
            "         followed by the reformulated query optimized for search.\n"
            "- If it does NOT require external documents, respond solely with the word 'NO'.\n"
            "- Do not include explanations, greetings, or any additional text.\n\n"
            "Example of expected format (if it requires documents):\n"
            "YES: What are the refund policies for company XYZ?"
        )

        try:
            decision_response = await self._llm.ainvoke([HumanMessage(content=decision_prompt)])
            decision_text = decision_response.content.strip().upper()

            if "YES" not in decision_text:
                return {'session_id': session_id}
        except Exception:
            pass

        _, question_ = decision_text.split("YES: ", 1)

        for rag_name, rag_retriever in self._rag_sources.items():
            try:
                retrieved_content = rag_retriever.retrieve_and_format(question_)
                rag_texts.append(f"--- Content from RAG {rag_name} [{retrieved_content}]")
            except Exception as e:
                rag_texts.append(f"--- RAG [{rag_name}] error loading information: {e} ---")

        return {
            "rag_query": question_,
            "rag_texts": rag_texts,
            "session_id": session_id
        }

    # --- Node 2: Prepara las tools de los MCPs y skills ---
    async def prepare_tools_node(self, state: AgentState) -> dict[str, Any]:
        """Collect local skills and fetch remote tools from active MCP servers."""
        available_tools = list(self._skills)
        mcp_error_warning = None

        if self._mcps:
            try:
                await self._start_mcp_client()
                mcp_tools = await self._mcp_manager.get_active_tools(self._mcps, self._mcp_client)
                available_tools.extend(mcp_tools)
            except Exception as e:
                mcp_error_warning = f"[Warning: Failed to load tools from MCP servers: {e}]"
                current_context = state.get("context", {})
                current_context["mcp_warning"] = mcp_error_warning

        return {
            "tools": available_tools
        }

    # --- Node 3: Consulta/actualiza Memory ---
    async def memory_node(self, state: AgentState) -> dict[str, Any]:
        """Load history or session variables from the configured memory system."""
        current_context = dict(state.get("context", {}))

        if self._memory:
            try:
                messages: list[BaseMessage] = state.get("messages", [])
                last_msg = messages[-1]
                session_id = state.get("session_id", "")
                await self._memory.add_message(session_id, last_msg)
                current_context = await self._memory.get_messages(session_id)
            except Exception as e:
                current_context["memory_error"] = str(e)

        return {
            "context": current_context,
            "memory_data": current_context
        }

    # --- Node 4: Llama al nodo de razonar ---
    async def reasoning_node(self, state: AgentState) -> dict[str, Any]:
        """Execute the core reasoning agent using the prepared RAG texts, tools, and memory."""
        messages = list(state.get("messages", []))
        rag_texts = state.get("rag_texts", [])
        tools = state.get("tools", [])
        current_context = state.get("context", {})
        memory_data = state.get("memory_data", None)

        # Construct system prompt with retrieved RAG knowledge
        system_prompt = "You are an autonomous AI assistant."
        if rag_texts:
            system_prompt += "\n\nRetrieved Knowledge (RAG):\n" + "\n".join(rag_texts)

        if "mcp_warning" in current_context:
            system_prompt += f"\n\n{current_context['mcp_warning']}"

        if memory_data:
            system_prompt += f"\n\nMemory Data:\n{memory_data}"

        # Instantiate the agent using create_agent
        react_agent = create_agent(
            model=self._llm,
            tools=tools,
            system_prompt=system_prompt,
        )

        # Invoke the react agent asynchronously with message history
        agent_response = await react_agent.ainvoke({"messages": messages})
        agent_messages = agent_response.get("messages", [])

        # Merge new responses with existing conversation messages
        updated_messages = messages + [msg for msg in agent_messages if msg not in messages]

        return {
            "messages": updated_messages,
            "context": current_context
        }

    # --- Node 5: Guarda la interacción en la memoria a largo plazo---
    async def save_memory_node(self, state: Any) -> dict[str, Any]:
        """Save the latest interaction (user input and assistant response) into memory."""
        if self._memory and hasattr(self._memory, "save_context"):
            messages = state.get("messages", [])
            if len(messages) >= 2:
                last_user_msg = ""
                last_ai_msg = ""

                for msg in reversed(messages):
                    if isinstance(msg, AIMessage) and not last_ai_msg:
                        last_ai_msg = msg.content
                    elif isinstance(msg, HumanMessage) and not last_user_msg:
                        last_user_msg = msg.content
                    if last_user_msg and last_ai_msg:
                        break

                if last_user_msg or last_ai_msg:
                    try:
                        self._memory.save_context({"input": last_user_msg}, {"output": last_ai_msg})
                    except Exception:
                        pass

        return {}

    def with_llm(self, config: LLMConfig) -> AgentBuilder:
        """Configure the primary LLM for the agent."""
        self._llm = ChatLiteLLM(
            model=config.model_name,
            temperature=config.temperature,
            api_base=config.api_base,
            api_key=get_settings().llm_api_key.get_secret_value()
        )
        return self

    def add_rag_source(self, name: str, retriever: BaseRetriever) -> AgentBuilder:
        """Add a RAG source to the agent's knowledge retrieval ecosystem."""
        self._rag_sources[name] = retriever
        return self

    def add_memory(self, memory: MemoryTypes) -> AgentBuilder:
        """Add a memory backend to the agent."""
        self._memory = memory
        return self

    def add_skill(self, skill: Any) -> AgentBuilder:
        """Add a custom skill or tool to the agent."""
        self._skills.append(skill)
        return self

    def add_mcp(self, mcp: MCPConnection) -> AgentBuilder:
        """Add a Model Context Protocol (MCP) server or client."""
        self._mcps.append(mcp)
        return self

    def build(self) -> CompiledStateGraph:
        """Build and compile the LangGraph workflow representing the agent.

        Returns:
            Compiled LangGraph workflow ready for execution.
        """
        workflow = StateGraph(self._state_schema)

        # Add specialized nodes to the StateGraph
        workflow.add_node("prepare_rag_query", self.prepare_rag_query_node)
        workflow.add_node("prepare_tools", self.prepare_tools_node)
        workflow.add_node("memory_node", self.memory_node) # Memoria largo plazo
        workflow.add_node("reasoning", self.reasoning_node)
        workflow.add_node("save_memory", self.save_memory_node) # Memoria corto plazo

        # Wire the sequential execution flow
        workflow.set_entry_point("prepare_rag_query")
        workflow.add_edge("prepare_rag_query", "prepare_tools")
        workflow.add_edge("prepare_tools", "memory_node")
        workflow.add_edge("memory_node", "reasoning")
        workflow.add_edge("reasoning", "save_memory")
        workflow.add_edge("save_memory", END)

        return workflow.compile()

    async def close(self) -> None:
        """Close active MCP connections gracefully."""
        if self._mcp_client and hasattr(self._mcp_client, "close"):
            await self._mcp_client.close()