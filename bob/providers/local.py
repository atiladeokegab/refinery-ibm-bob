from __future__ import annotations

import json
import os
from typing import Generator

import requests

from bob.providers import BaseProvider


class OllamaProvider(BaseProvider):
    def __init__(self) -> None:
        self._url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
        self._model = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")

    def _augment(self, prompt: str) -> str:
        try:
            from bob.rag.retriever import retrieve
            query = self._extract_query(prompt)
            chunks = retrieve(query, top_k=3)
            context = "\n\n---\n\n".join(f"[{c.source}]\n{c.text}" for c in chunks)
            return prompt.replace("{context}", context)
        except Exception:
            return prompt.replace("{context}", "(No regulatory context retrieved)")

    def _extract_query(self, prompt: str) -> str:
        import re
        m = re.search(r"Semantic changes detected:\n(.+?)(?:\n\nRegulatory|$)", prompt, re.DOTALL)
        if m:
            return m.group(1).strip()[:300]
        return "COBOL program change risk assessment"

    def complete(self, prompt: str) -> str:
        return "".join(self.stream(prompt))

    def stream(self, prompt: str) -> Generator[str, None, None]:
        augmented = self._augment(prompt)
        resp = requests.post(
            f"{self._url}/api/generate",
            json={"model": self._model, "prompt": augmented, "stream": True},
            timeout=120,
            stream=True,
        )
        resp.raise_for_status()
        for line in resp.iter_lines():
            if not line:
                continue
            try:
                chunk = json.loads(line)
                token = chunk.get("response", "")
                if token:
                    yield token
                if chunk.get("done"):
                    break
            except json.JSONDecodeError:
                continue
