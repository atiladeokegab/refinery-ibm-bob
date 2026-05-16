from __future__ import annotations

import re
from pathlib import Path
from typing import NamedTuple

import numpy as np

from bob.rag.embedder import embed

_KB_DIR = Path(__file__).parent / "knowledge_base"
_CHUNK_SIZE = 400  # chars per chunk


class Chunk(NamedTuple):
    text: str
    source: str


_INDEX: list[tuple[Chunk, list[float]]] | None = None


def _chunk_markdown(text: str, source: str) -> list[Chunk]:
    # Split on double newlines, keep chunks above 80 chars
    parts = re.split(r"\n{2,}", text.strip())
    chunks = []
    buf = ""
    for part in parts:
        if len(buf) + len(part) < _CHUNK_SIZE:
            buf = (buf + "\n\n" + part).strip()
        else:
            if buf:
                chunks.append(Chunk(buf, source))
            buf = part
    if buf:
        chunks.append(Chunk(buf, source))
    return chunks


def _build_index() -> list[tuple[Chunk, list[float]]]:
    index = []
    for md_file in sorted(_KB_DIR.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        for chunk in _chunk_markdown(text, md_file.stem):
            vec = embed(chunk.text)
            index.append((chunk, vec))
    return index


def _cosine(a: list[float], b: list[float]) -> float:
    va = np.array(a, dtype=np.float32)
    vb = np.array(b, dtype=np.float32)
    denom = np.linalg.norm(va) * np.linalg.norm(vb)
    return float(np.dot(va, vb) / denom) if denom > 0 else 0.0


def retrieve(query: str, top_k: int = 3) -> list[Chunk]:
    global _INDEX
    if _INDEX is None:
        _INDEX = _build_index()
    q_vec = embed(query)
    scored = [(chunk, _cosine(q_vec, vec)) for chunk, vec in _INDEX]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [chunk for chunk, _ in scored[:top_k]]
