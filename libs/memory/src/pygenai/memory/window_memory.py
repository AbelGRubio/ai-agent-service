"""WindowMemory: limits conversation history to a context window."""

from pygenai.core.base_memory import MemoryStore
from pygenai.core.models import ConversationState, Message


class WindowMemory(MemoryStore):
    """
    Memory store that maintains a sliding window of recent messages.

    Keeps only the most recent messages within a token limit or turn limit
    to prevent context overflow. Older messages are discarded.
    """

    def __init__(self, max_tokens: int = 4096, max_turns: int | None = None):
        """
        Initialize WindowMemory.

        Args:
            max_tokens: Maximum tokens to keep in the window (default: 4096).
            max_turns: Optional maximum number of turns (message pairs) to keep.
        """
        self._max_tokens = max_tokens
        self._max_turns = max_turns
        self._sessions: dict[str, ConversationState] = {}

    async def add_message(self, session_id: str, message: Message) -> None:
        """
        Add a message and trim window if necessary.

        Args:
            session_id: The session identifier.
            message: The message to add.
        """
        if session_id not in self._sessions:
            self._sessions[session_id] = ConversationState(session_id=session_id)

        state = self._sessions[session_id]
        state.messages.append(message)
        state.total_tokens += message.tokens

        await self._trim_window(session_id)

    async def get_messages(self, session_id: str) -> list[Message]:
        """
        Retrieve messages within the current window.

        Args:
            session_id: The session identifier.

        Returns:
            List of messages in the window.
        """
        if session_id not in self._sessions:
            return []
        return self._sessions[session_id].messages

    async def get_state(self, session_id: str) -> ConversationState:
        """
        Retrieve the conversation state within the window.

        Args:
            session_id: The session identifier.

        Returns:
            The conversation state with windowed messages.
        """
        if session_id not in self._sessions:
            return ConversationState(session_id=session_id)
        return self._sessions[session_id]

    async def add_summary(self, session_id: str, summary) -> None:
        """
        Add a summary (discarded messages stored separately).

        Args:
            session_id: The session identifier.
            summary: The summary record.
        """
        if session_id not in self._sessions:
            self._sessions[session_id] = ConversationState(session_id=session_id)
        self._sessions[session_id].summaries.append(summary)

    async def clear_messages(self, session_id: str) -> None:
        """
        Clear all messages from the window.

        Args:
            session_id: The session identifier.
        """
        if session_id in self._sessions:
            self._sessions[session_id].messages.clear()
            self._sessions[session_id].total_tokens = 0

    async def delete_session(self, session_id: str) -> None:
        """
        Delete the entire session.

        Args:
            session_id: The session identifier.
        """
        self._sessions.pop(session_id, None)

    async def _trim_window(self, session_id: str) -> None:
        """
        Trim messages from the beginning if they exceed limits.

        Args:
            session_id: The session identifier.
        """
        state = self._sessions[session_id]

        if self._max_turns and len(state.messages) > self._max_turns:
            removed_count = len(state.messages) - self._max_turns
            removed_messages = state.messages[:removed_count]
            removed_tokens = sum(m.tokens for m in removed_messages)
            state.messages = state.messages[removed_count:]
            state.total_tokens -= removed_tokens

        while state.total_tokens > self._max_tokens and state.messages:
            msg = state.messages.pop(0)
            state.total_tokens -= msg.tokens
