from __future__ import annotations
import os
from bob.providers import BaseProvider


class OpenAIProvider(BaseProvider):
    def __init__(self) -> None:
        from openai import OpenAI
        self._client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def complete(self, prompt: str) -> str:
        resp = self._client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4o"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
        )
        return resp.choices[0].message.content
