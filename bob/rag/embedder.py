from __future__ import annotations

import os
import requests


_EMBED_MODEL = os.environ.get("OLLAMA_EMBED_MODEL", "nomic-embed-text")
_OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")


def embed(text: str) -> list[float]:
    resp = requests.post(
        f"{_OLLAMA_URL}/api/embed",
        json={"model": _EMBED_MODEL, "input": text},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    # /api/embed returns {"embeddings": [[...]]} (list of lists)
    return data["embeddings"][0]
