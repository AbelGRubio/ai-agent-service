"""Token counting utilities using tiktoken."""

import tiktoken


class TokenCounter:
    """Utility for counting tokens in text using tiktoken."""

    _encoding = None

    @classmethod
    def _get_encoding(cls):
        """Lazy load the encoding."""
        if cls._encoding is None:
            cls._encoding = tiktoken.get_encoding("cl100k_base")
        return cls._encoding

    @classmethod
    def count(cls, text: str) -> int:
        """
        Count tokens in the given text.

        Args:
            text: The text to count tokens for.

        Returns:
            Number of tokens in the text.
        """
        encoding = cls._get_encoding()
        return len(encoding.encode(text))

    @classmethod
    def count_messages(cls, messages: list[dict]) -> int:
        """
        Count tokens in a list of OpenAI-style messages.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.

        Returns:
            Estimated token count.
        """
        encoding = cls._get_encoding()
        total = 0

        for msg in messages:
            total += 4  # overhead per message
            if isinstance(msg, dict):
                total += len(encoding.encode(msg.get("content", "")))
            elif hasattr(msg, "content"):
                total += len(encoding.encode(msg.content))

        total += 2  # extra overhead
        return total
