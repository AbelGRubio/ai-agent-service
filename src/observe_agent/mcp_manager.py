import asyncio
from typing import Dict
from mcp import ClientSession
from langchain_mcp_adapters.client import MultiServerMCPClient

class MCPManager:
    def __init__(self):
        self.sessions: Dict[str, ClientSession] = {}
        self.lock = asyncio.Lock()

    async def get_session(self, client: MultiServerMCPClient, name: str) -> ClientSession:
        async with self.lock:
            if name not in self.sessions:
                # Abrimos la sesión y la guardamos para que persista
                session = await client.session(name).__aenter__()
                self.sessions[name] = session
            return self.sessions[name]

    async def close_all(self):
        # Cierra todas las sesiones activas
        for session in self.sessions.values():
            await session.__aexit__(None, None, None)
        self.sessions.clear()


app_mcp_manager = MCPManager()
