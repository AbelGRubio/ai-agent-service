"""MCP manager: lifecycle and caching utilities for MCP sessions/tools.

This module provides a singleton `MCPManager` that keeps MCP sessions open
across the agent runtime and caches tool lists per MCP configuration hash.
The manager is safe for concurrent access via an `asyncio.Lock`.

========================================================================================================================
Name:         apps/agent/src/observe_agent/mcp_manager.py
Description:  Manage MCP ClientSession lifecycle and tool caching.
Project:      Observe me
Date:         2026-06-19 00:00:00
Status:       Development

Copyright ©2026. All rights reserved.
========================================================================================================================
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from functools import lru_cache
from typing import Any, Dict, List, Optional

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession
from observe_core.logger import get_logger

logger = get_logger(__name__)


class MCPManager:
    """Manage MCP sessions and cache tools per configuration.

    Attributes:
        sessions: Mapping of server name -> active `ClientSession`.
        tools_cache: Mapping of config-hash -> list of tools loaded for that
            configuration.
        current_config_hash: Last seen configuration hash, used to detect
            configuration changes.
        lock: Asyncio lock to protect concurrent access.
    """

    def __init__(self) -> None:
        self.sessions: Dict[str, ClientSession] = {}
        self.tools_cache: Dict[str, List[Any]] = {}  # Cache de herramientas
        self.current_config_hash: Optional[str] = None
        self.lock = asyncio.Lock()

    def _get_hash(self, mcp_config: Dict[str, Any]) -> str:
        """Generate a stable hash for the given MCP configuration mapping."""
        config_str = json.dumps(mcp_config, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()

    async def get_session(self, client: MultiServerMCPClient, name: str) -> ClientSession:
        """Return an active `ClientSession` for `name`, creating it if missing.

        The session is created by entering the async context manager returned by
        `client.session(name)` and stored for reuse until `close_all` is called.
        """

        async with self.lock:
            if name not in self.sessions:
                # Open the async context and retain the session reference so it
                # can be reused across calls.
                session = await client.session(name).__aenter__()
                self.sessions[name] = session
            return self.sessions[name]

    async def close_all(self) -> None:
        """Close and clear all active sessions.

        This method attempts to call the async context exit of each session.
        It tolerates different session APIs (async __aexit__ or sync `close`).
        """

        async with self.lock:
            for session in list(self.sessions.values()):
                try:
                    await session.__aexit__(None, None, None)
                except Exception:
                    # Best-effort: attempt `.close()` if available.
                    try:
                        maybe = session.close()
                        if asyncio.iscoroutine(maybe):
                            await maybe
                    except Exception:
                        logger.debug("Failed to gracefully close session", exc_info=True)

            self.sessions.clear()

    async def get_active_tools(self, mcp_config: Dict[str, Any], mcp_client: MultiServerMCPClient) -> List[Any]:
        """Load and return tools for the active MCP configuration.

        The function computes a hash of `mcp_config` and returns cached tools if
        available. When the configuration changes, existing sessions are
        closed and the cache is refreshed.
        """

        async with self.lock:
            new_hash = self._get_hash(mcp_config)

            # If configuration changed, close old sessions and reset cache
            if self.current_config_hash != new_hash:
                await self.close_all()
                self.current_config_hash = new_hash

            if new_hash in self.tools_cache:
                return self.tools_cache[new_hash]

            all_tools: List[Any] = []
            for name in mcp_config:
                # Ensure we have an active session for each configured server
                session = await self.get_session(mcp_client, name)
                # Load the tools exposed by the session
                server_tools = await load_mcp_tools(session)
                all_tools.extend(server_tools)

            self.tools_cache[new_hash] = all_tools
            return all_tools


@lru_cache(maxsize=1)
def get_mcp_manager() -> MCPManager:
    """Return a cached MCPManager singleton.

    The manager is created once per process and reused by callers.
    """
    logger.info("Creating MCPManager singleton")
    return MCPManager()
