from __future__ import annotations

from dataclasses import dataclass, field
from langchain.agents import create_agent
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_litellm import ChatLiteLLM
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import Connection, StreamableHttpConnection, StdioConnection, SSEConnection, \
    WebsocketConnection
from langgraph.graph import StateGraph, END
from typing import Any, Callable, Dict, List, Optional, Union
from typing_extensions import TypeAlias, TypedDict

from pygenai.settings import get_settings
from pygenai.utils.mcp_manager import get_mcp_manager
import litellm

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


@dataclass
class RAGConfig:
    """Configuration class for RAG (Retrieval-Augmented Generation) sources."""
    files: List[str]
    llm: Optional[LLMConfig] = None
    chunk_size: int = 1000
    chunk_overlap: int = 200


class AgentState(TypedDict):
    """Defines the state structure for the LangGraph agent."""
    messages: list[BaseMessage]
    context: dict[str, Any]


class AgentBuilder:
    """Builder class for constructing LangGraph agents following SOLID principles.

    Allows fluent configuration of LLMs, RAG sources, memory systems, MCPs, and skills.
    """

    def __init__(self) -> None:
        """Initialize the AgentBuilder with empty configurations."""
        # self._llm_config: Optional[LLMConfig] = None
        self._rag_sources: Dict[str, RAGConfig] = {}
        self._memory: Optional[Any] = None
        self._skills: list[Any] = []
        self._mcps: list[MCPConnection] = []
        self._custom_reasoning_flow: Optional[Callable[[AgentState, Dict[str, Any]], dict[str, Any]]] = None
        self._mcp_client: Optional[MultiServerMCPClient] = None
        self._mcp_manager = get_mcp_manager()
        self._define_default_llm()

    def _define_default_llm(self) -> None:
        """Define a default LLM configuration if none is provided."""
        settings = get_settings()

        self._llm = ChatLiteLLM(
            model="gemini/gemini-3.6-flash",
            temperature=0.7,
            api_key=settings.llm_api_key.get_secret_value(),
            api_base=settings.model_base_url
        )

    async def _start_mcp_client(self) -> None:
        """Initialize the MultiServerMCPClient if MCP configurations are provided."""
        if self._mcps and not self._mcp_client:
            self._mcp_client = MultiServerMCPClient(self._mcps)  # type: ignore[arg-type]

        await self._mcp_manager.get_active_tools(self._mcps, self._mcp_client)

    # Default reasoning node incorporating memory, RAG, skills, and MCPs
    async def default_reasoning_node(self, state: AgentState) -> dict[str, Any]:
        """Execute the core reasoning step using LangChain's create_agent, integrating RAGs, skills, MCPs, and memory."""
        messages = list(state["messages"])
        current_context = state.get("context", {})

        # 1. Retrieve history or extra context from memory if available
        if self._memory and hasattr(self._memory, "load_memory_variables"):
            memory_data = self._memory.load_memory_variables({})
            if memory_data:
                current_context.update(memory_data)

        # 2. Gather and read RAG sources information if configured
        rag_texts = []

        for rag_name, rag_cfg in self._rag_sources.items():
            for file_path in rag_cfg.files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        rag_texts.append(f"--- Content from RAG [{rag_name} : {file_path}] ---\n{f.read()}")
                except Exception as e:
                    rag_texts.append(f"--- RAG [{rag_name}] error loading file {file_path}: {e} ---")

        # 3. Construct system prompt including RAG knowledge if available
        system_prompt = f"You are an autonomous AI assistant."
        if rag_texts:
            system_prompt += "\n\nRetrieved Knowledge (RAG):\n" + "\n".join(rag_texts)

        available_tools = list(self._skills)

        # 5. Establish MultiServerMCPClient connection and load remote MCP tools if configured
        if self._mcps:
            await self._start_mcp_client()
            try:
                mcp_tools = await self._mcp_manager.get_active_tools(self._mcps, self._mcp_client)
                available_tools.extend(mcp_tools)
            except Exception as e:
                system_prompt += f"\n\n[Warning: Failed to load tools from MCP servers: {e}]"

        # 4. Instantiate the agent using create_agent
        react_agent = create_agent(
            model=self._llm,
            tools=available_tools,
            system_prompt=system_prompt,
        )

        # 5. Invoke the react agent asynchronously with the message history
        agent_response = await react_agent.ainvoke({"messages": messages})
        agent_messages = agent_response.get("messages", [])

        # Merge new responses with existing conversation messages
        updated_messages = messages + [msg for msg in agent_messages if msg not in messages]

        # 6. Save interaction to memory if supported
        if self._memory and hasattr(self._memory, "save_context"):
            if messages and updated_messages:
                last_user_msg = messages[-1].content if isinstance(messages[-1], HumanMessage) else ""
                last_ai_msg = updated_messages[-1].content if isinstance(updated_messages[-1], AIMessage) else ""
                self._memory.save_context({"input": last_user_msg}, {"output": last_ai_msg})

        return {
            "messages": updated_messages,
            "context": current_context
        }

    def with_llm(self, config: LLMConfig) -> AgentBuilder:
        """Configure the primary LLM for the agent.

        Args:
            config: LLM configuration instance.

        Returns:
            AgentBuilder: Self instance for method chaining.
        """
        self._llm = ChatLiteLLM(
            model=config.model_name,
            temperature=config.temperature,
            api_base=config.api_base,
            api_key=get_settings().llm_api_key.get_secret_value()
        )
        return self

    def add_rag_source(self, name: str, config: RAGConfig) -> AgentBuilder:
        """Add a RAG source to the agent's knowledge retrieval ecosystem.

        Args:
            name: Unique identifier for the RAG source.
            config: RAG configuration instance.

        Returns:
            AgentBuilder: Self instance for method chaining.
        """
        self._rag_sources[name] = config
        return self

    def add_memory(self, memory: Any) -> AgentBuilder:
        """Add a memory backend to the agent.

        Args:
            memory: Memory provider or configuration instance.

        Returns:
            AgentBuilder: Self instance for method chaining.
        """
        self._memory = memory
        return self

    def add_skill(self, skill: Any) -> AgentBuilder:
        """Add a custom skill or tool to the agent.

        Args:
            skill: Skill definition or executable tool.

        Returns:
            AgentBuilder: Self instance for method chaining.
        """
        self._skills.append(skill)
        return self

    def add_mcp(self, mcp: Connection) -> AgentBuilder:
        """Add a Model Context Protocol (MCP) server or client.

        Args:
            mcp: MCP connection configuration.

        Returns:
            AgentBuilder: Self instance for method chaining.
        """
        self._mcps.append(mcp)
        return self

    def set_reasoning_flow(
            self, flow_fn: Callable[[AgentState, Dict[str, Any]], dict[str, Any]]
    ) -> AgentBuilder:
        """Define a custom reasoning flow for the agent.

        Args:
            flow_fn: A callable defining custom state transitions or logic.

        Returns:
            AgentBuilder: Self instance for method chaining.
        """
        self._custom_reasoning_flow = flow_fn
        return self

    def build(self) -> Any:
        """Build and compile the LangGraph workflow representing the agent.

        Returns:
            Compiled LangGraph workflow ready for execution.

        Raises:
            ValueError: If mandatory configurations (such as primary LLM) are missing.
        """
        # if not self._llm_config:
        #     raise ValueError("Primary LLM configuration is required to build the agent.")

        # Initialize the LangGraph StateGraph
        workflow = StateGraph(AgentState)

        # Bundle available resources to be accessible during execution
        agent_resources = {
            "llm": self._llm,
            "rag_sources": self._rag_sources,
            "memory": self._memory,
            "skills": self._skills,
            "mcps": self._mcps,
        }

        # Determine which reasoning logic to use (Custom vs Default)
        if self._custom_reasoning_flow:
            def custom_node_wrapper(state: AgentState) -> dict[str, Any]:
                return self._custom_reasoning_flow(state, agent_resources)

            workflow.add_node("reasoning", custom_node_wrapper)
        else:
            workflow.add_node("reasoning", self.default_reasoning_node)

        # Add nodes and edges to the graph structure
        workflow.set_entry_point("reasoning")
        workflow.add_edge("reasoning", END)

        return workflow.compile()

    async def close(self) -> None:
        """Close active MCP connections gracefully."""
        if self._mcp_client and hasattr(self._mcp_client, "close"):
            await self._mcp_client.close()
