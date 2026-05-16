from __future__ import annotations
from abc import ABC, abstractmethod


class BaseProvider(ABC):
    @abstractmethod
    def complete(self, prompt: str) -> str:
        """Send prompt to LLM, return raw text response."""
