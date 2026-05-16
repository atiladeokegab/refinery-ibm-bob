from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from portal.auth import _db_path, verify_session_token
from portal.db import get_record_by_ref_id

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []
    token: str


def _build_system_prompt(record) -> str:
    try:
        affected = json.loads(record.affected_systems_json or "[]")
    except Exception:
        affected = []
    affected_str = ", ".join(affected[:10]) or "none identified"
    signed = f"Signed off by {record.signed_by}" if record.signed_by else "Not yet signed off"

    return (
        f"You are a risk analyst embedded in Refinery, an independent verification tool for AI-modified COBOL programs. "
        f"A Chief Risk Officer is reviewing the following audit record and will ask you questions. "
        f"Answer in plain English — no COBOL jargon, no acronyms without explanation. "
        f"Be direct, specific, and reference DORA Article 28 or FCA regulations where relevant.\n\n"
        f"AUDIT RECORD:\n"
        f"- Program: {record.program}\n"
        f"- Verdict: {record.verdict}\n"
        f"- Risk Score: {record.risk_score}/100\n"
        f"- Blast Radius Score: {record.blast_radius_score}/100\n"
        f"- Affected Downstream Systems: {affected_str}\n"
        f"- Risk Assessment: {record.bob_headline or 'Not yet assessed'}\n"
        f"- Signature Status: {signed}\n"
        f"- Date: {record.date}\n"
    )


def _build_rag_context(query: str) -> str:
    try:
        from bob.rag.retriever import retrieve
        chunks = retrieve(query, top_k=3)
        return "\n\n---\n\n".join(f"[{c.source}]\n{c.text}" for c in chunks)
    except Exception:
        return ""


def _build_full_prompt(system: str, rag_context: str, history: list[dict], message: str) -> str:
    parts = [system]
    if rag_context:
        parts.append(f"\nREGULATORY CONTEXT:\n{rag_context}")
    parts.append("\nCONVERSATION:")
    for turn in history[-6:]:
        role = "CRO" if turn["role"] == "user" else "Analyst"
        parts.append(f"{role}: {turn['content']}")
    parts.append(f"CRO: {message}")
    parts.append("Analyst:")
    return "\n".join(parts)


@router.post("/api/audits/{ref_id}/chat")
def chat(
    ref_id: str,
    body: ChatRequest,
    db: Path = Depends(_db_path),
):
    payload = verify_session_token(body.token)
    if not payload:
        raise HTTPException(401, "Invalid or expired token")

    record = get_record_by_ref_id(ref_id, db_path=db)
    if not record:
        raise HTTPException(404, f"No record: {ref_id}")

    def _stream():
        # Tell the browser immediately so the UI shows a thinking state
        yield f"data: {json.dumps({'thinking': True})}\n\n"
        try:
            import requests as _req
            system = _build_system_prompt(record)
            rag_context = _build_rag_context(body.message)
            prompt = _build_full_prompt(system, rag_context, body.history, body.message)

            ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
            ollama_model = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")
            # (connect_timeout, read_timeout): fail fast if Ollama is down,
            # but allow up to 120 s for the model to produce its first token.
            resp = _req.post(
                f"{ollama_url}/api/generate",
                json={"model": ollama_model, "prompt": prompt, "stream": True},
                timeout=(10, 120),
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
                        yield f"data: {json.dumps({'token': token})}\n\n"
                    if chunk.get("done"):
                        yield f"data: {json.dumps({'done': True})}\n\n"
                        break
                except Exception:
                    continue
        except Exception as exc:
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(
        _stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
