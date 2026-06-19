import asyncio
import hashlib
import json
from functools import lru_cache
from typing import Any

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession


class MCPManager:
    def __init__(self):
        self.sessions: dict[str, ClientSession] = {}
        self.tools_cache: dict[str, list[Any]] = {}  # Cache de herramientas
        self.current_config_hash = None
        self.lock = asyncio.Lock()

    def _get_hash(self, mcp_config: dict[str, Any]) -> str:
        # Generamos un hash único basado en la configuración actual
        config_str = json.dumps(mcp_config, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()

    async def get_session(self, client: MultiServerMCPClient, name: str) -> ClientSession:
        async with self.lock:
            if name not in self.sessions:
                # Abrimos la sesión y la guardamos para que persista
                session = await client.session(name).__aenter__()
                self.sessions[name] = session
            return self.sessions[name]

    def close_all(self):
        # Cierra todas las sesiones activas
        # for session in self.sessions.values():
        #     await session.__aexit__(None, None, None)
        self.sessions.clear()

    async def get_active_tools(self, mcp_config: dict[str, Any], mcp_client: MultiServerMCPClient):
        async with self.lock:
            new_hash = self._get_hash(mcp_config)

            # Si la config cambió, limpiamos sesiones antiguas (o podrías hacer lógica diferencial)
            if self.current_config_hash != new_hash:
                await self.close_all()
                self.current_config_hash = new_hash

            if new_hash in self.tools_cache:
                return self.tools_cache[new_hash]

            all_tools = []
            for name in mcp_config:
                session = self.get_session(mcp_client, name)
                # Obtenemos herramientas de la sesión abierta
                server_tools = await load_mcp_tools(session)
                all_tools.extend(server_tools)

            self.tools_cache[new_hash] = all_tools
            return all_tools


@lru_cache(maxsize=1)
def get_mcp_manager() -> MCPManager:
    """Return a cached settings instance."""
    print("MCP Manager")
    return MCPManager()
