import httpx

from observe_core.logger_api import get_logger
from observe_agent.settings import get_settings

logger = get_logger(__name__)


async def get_jwt_token() -> str:
    """Retrieve a JWT token for outbound MCP calls."""
    settings = get_settings()
    if not settings.client_id or not settings.client_secret:
        raise ValueError("CLIENT_ID and CLIENT_SECRET are required when JWT protection is enabled")

    async with httpx.AsyncClient() as client:
        response = await client.post(  # await aquí
            settings.jwt_url,
            data={"grant_type": "client_credentials"},
            auth=(settings.client_id, settings.client_secret),
            timeout=10.0,
        )
    response.raise_for_status()
    payload = response.json()
    token = payload.get("access_token")
    if not token:
        raise ValueError("JWT response does not include access_token")
    return token

