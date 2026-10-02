"""Core data models for the memory system."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4


class MessageRole(StrEnum):
    """Role of the message sender."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class Message:
    """
    Represents a single message in a conversation.

    Attributes:
        id: Unique identifier for the message.
        role: Role of the sender (user, assistant, system).
        content: The message text content.
        tokens: Number of tokens in the message (estimated via tiktoken).
        metadata: Additional metadata (e.g., source, model, confidence).
        timestamp: When the message was created.
    """

    role: MessageRole
    content: str
    id: str = field(default_factory=lambda: str(uuid4()))
    tokens: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "id": self.id,
            "role": self.role.value,
            "content": self.content,
            "tokens": self.tokens,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Message:
        """Create message from dictionary."""
        return cls(
            id=data.get("id", str(uuid4())),
            role=MessageRole(data["role"]),
            content=data["content"],
            tokens=data.get("tokens", 0),
            metadata=data.get("metadata", {}),
            timestamp=datetime.fromisoformat(data["timestamp"])
            if isinstance(data.get("timestamp"), str)
            else data.get("timestamp", datetime.utcnow()),
        )


@dataclass
class SummaryRecord:
    """
    Represents a compressed summary of past conversation segments.

    Attributes:
        id: Unique identifier for the summary.
        messages_count: Number of original messages summarized.
        original_tokens: Total tokens in the summarized messages.
        summary: The condensed summary text.
        metadata: Original context (e.g., date range, topics).
        timestamp: When the summary was created.
    """

    summary: str
    messages_count: int = 0
    original_tokens: int = 0
    id: str = field(default_factory=lambda: str(uuid4()))
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Convert summary to dictionary."""
        return {
            "id": self.id,
            "summary": self.summary,
            "messages_count": self.messages_count,
            "original_tokens": self.original_tokens,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SummaryRecord:
        """Create summary from dictionary."""
        return cls(
            id=data.get("id", str(uuid4())),
            summary=data["summary"],
            messages_count=data.get("messages_count", 0),
            original_tokens=data.get("original_tokens", 0),
            metadata=data.get("metadata", {}),
            timestamp=datetime.fromisoformat(data["timestamp"])
            if isinstance(data.get("timestamp"), str)
            else data.get("timestamp", datetime.utcnow()),
        )


@dataclass
class ConversationState:
    """
    Represents the complete state of a conversation.

    Attributes:
        session_id: Unique session identifier.
        messages: Current active messages in the conversation.
        summaries: Historical summaries of past conversation segments.
        total_tokens: Total tokens across all messages.
        metadata: Session-level metadata.
    """

    session_id: str
    messages: list[Message] = field(default_factory=list)
    summaries: list[SummaryRecord] = field(default_factory=list)
    total_tokens: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert state to dictionary."""
        return {
            "session_id": self.session_id,
            "messages": [m.to_dict() for m in self.messages],
            "summaries": [s.to_dict() for s in self.summaries],
            "total_tokens": self.total_tokens,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ConversationState:
        """Create state from dictionary."""
        return cls(
            session_id=data["session_id"],
            messages=[Message.from_dict(m) for m in data.get("messages", [])],
            summaries=[SummaryRecord.from_dict(s) for s in data.get("summaries", [])],
            total_tokens=data.get("total_tokens", 0),
            metadata=data.get("metadata", {}),
        )
