"""Agent settings and default runtime configuration."""

from functools import lru_cache

from observe_core.custom_settings import CustomSettings
from pydantic import Field, SecretStr
from pydantic_settings import SettingsConfigDict

__version__ = "0.1.0"


class AgentSettings(CustomSettings):
    """Settings parsed from environment variables for the agent runtime."""

    __use_conf_file__: bool = False

    jwt_protected: bool = Field(default=True, alias="JWT_PROTECTED")
    jwt_url: str = Field(
        default="http://localhost:9000/api/token",
        alias="JWT_URL",
    )
    client_id: str | None = Field(default=None, alias="CLIENT_ID")
    client_secret: str | None = Field(default=None, alias="CLIENT_SECRET")

    mcp_url: str = Field(default="http://localhost:8000/mcp", alias="MCP_LOCAL_URL")

    model_name: str = Field(default="gpt-4o", alias="MODEL_NAME")
    openai_api_key: SecretStr = Field(default=None, alias="OPENAI_API_KEY")
    llm_api_key: SecretStr = Field(default=None, alias="LLM_API_KEY")
    model_base_url: str | None = Field(default="http://localhost:5000", alias="MODEL_BASE_URL")

    model_config = SettingsConfigDict(
        env_prefix="",
        populate_by_name=True,
        extra="ignore",
    )


def default__mcp_config(settings: AgentSettings) -> dict:
    """Build default MCP configuration using parsed settings values."""
    return {
        "observe-mcp": {
            "url": settings.mcp_url,
            "headers": {},
            "transport": "http",
        }
    }


@lru_cache(maxsize=1)
def get_settings() -> AgentSettings:
    """Return a cached settings instance."""
    return AgentSettings()
