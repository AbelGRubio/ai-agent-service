
from copilotkit import CopilotKitState
from pydantic import BaseModel, Field

from observe_agent.mcp_types import MCPConfig
from observe_core.logger_api import get_logger


logger = get_logger(__name__)

class ConnectionConfig(BaseModel):
    """Normalized MCP connection payload."""

    url: str
    headers: dict[str, str] = Field(default_factory=dict)
    transport: str = Field(default="http")

    def add_token(self, token: str):
        self.headers["Authorization"] = f"Bearer {token}"


class AgentState(CopilotKitState):
    """Agent state passed across the langgraph workflow.

    In this instance, we're inheriting from CopilotKitState, which will bring in
    the CopilotKitState fields. We're also adding a custom field, `mcp_config`,
    which will be used to configure MCP services for the agent.
    """

    # Define mcp_config as an optional field without skipping validation
    mcp_config: MCPConfig | None
    openai_api_key: str | None
    rag_context: str | None
