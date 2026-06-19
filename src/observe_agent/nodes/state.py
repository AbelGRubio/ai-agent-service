"""Node-local state models for the agent workflow.

========================================================================================================================
Name:         apps/agent/src/observe_agent/nodes/state.py
Description:  Pydantic models and state container types used by nodes.
Project:      Observe me
Date:         2026-06-19 00:00:00
Status:       Development

Copyright ©2026. All rights reserved.
========================================================================================================================
"""

from copilotkit import CopilotKitState
from observe_core.logger import get_logger
from pydantic import BaseModel, Field

from observe_agent.mcp_types import MCPConfig

logger = get_logger(__name__)


class ConnectionConfig(BaseModel):
    """Normalized MCP connection payload.

    Attributes:
        url: Base URL for the MCP server.
        headers: HTTP headers to send with requests.
        transport: Transport scheme (e.g., 'http', 'grpc').
    """

    url: str
    headers: dict[str, str] = Field(default_factory=dict)
    transport: str = Field(default="http")

    def add_token(self, token: str) -> None:
        """Attach a bearer token to the connection headers."""
        self.headers["Authorization"] = f"Bearer {token}"


class AgentState(CopilotKitState):
    """Agent state passed across the langgraph workflow.

    Inherits from `CopilotKitState` and extends it with agent-specific keys
    used by the nodes in this package.
    """

    mcp_config: MCPConfig | None
    openai_api_key: str | None
    rag_context: str | None
