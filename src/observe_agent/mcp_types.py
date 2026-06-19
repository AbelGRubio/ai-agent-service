"""Typed structures for MCP connection configuration."""

from typing import Literal, TypedDict


class StdioConnection(TypedDict):
    """MCP connection over stdio transport."""

    command: str
    args: list[str]
    transport: Literal["stdio"]


class SSEConnection(TypedDict):
    """MCP connection over SSE transport."""

    url: str
    transport: Literal["sse"]


class HTTPConnection(TypedDict):
    """MCP connection over HTTP transport."""

    url: str
    headers: dict[str, str]
    transport: Literal["http"]


MCPConfig = dict[str, StdioConnection | SSEConnection | HTTPConnection]
