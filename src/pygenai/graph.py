"""Main entry point for the CopilotKit agent graph."""

from pygenai.agent_builder import AgentBuilder
from libs.core.src.pygenai.core.logger import get_logger
from pygenai.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()

agent_builder = AgentBuilder()

# Compile the workflow graph
graph = agent_builder.build()
