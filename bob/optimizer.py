"""bob.optimizer — ask IBM Granite to optimise a COBOL program.

Falls back to a canned "safe" edit if no watsonx credentials are set,
so the demo works offline.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

_OPTIMIZE_PROMPT_BASE = """\
You are an expert COBOL engineer optimising legacy mainframe programs for IBM z/Architecture.

Rewrite the COBOL program below with these specific optimisations ONLY:
1. Change numeric WORKING-STORAGE fields from display format (PIC 9...) to COMP-3 \
(packed decimal) where appropriate — this reduces CPU by ~6% per field on z/Architecture.
2. Do NOT change any arithmetic expressions, constants, or business logic.
3. Do NOT add, remove, or reorder any PERFORM statements.
4. Return ONLY the complete rewritten COBOL program — no explanation, no markdown."""


def _build_optimize_prompt(source: str, rag_context: str = "") -> str:
    prompt = _OPTIMIZE_PROMPT_BASE
    if rag_context:
        prompt += f"\n\nKNOWN PATTERNS TO AVOID (from prior audits):\n{rag_context}"
    prompt += f"\n\nCOBOL PROGRAM:\n{source}\n"
    return prompt


def _get_rag_context(program_name: str, source: str) -> str:
    try:
        # Lazy import: RAG failures must not break optimizer module import.
        from bob.rag.retriever import retrieve
        query = f"COBOL optimization mistakes {program_name}"
        if "COMPUTE" in source.upper():
            query += " financial calculations COMPUTE"
        chunks = retrieve(query, top_k=4)
        if not chunks:
            return ""
        lines = "\n".join(f"- {c.text[:300]}" for c in chunks)
        return lines
    except Exception:
        return ""


def _call_granite(prompt: str) -> str:
    """Call IBM watsonx Granite with a fully-formatted prompt. Raises if credentials missing."""
    import requests

    api_key = os.environ.get("WATSONX_API_KEY")
    project_id = os.environ.get("WATSONX_PROJECT_ID")
    if not api_key or not project_id:
        raise RuntimeError("WATSONX_API_KEY and WATSONX_PROJECT_ID must be set")
    url = os.environ.get("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
    model = os.environ.get("WATSONX_MODEL", "ibm/granite-3-8b-instruct")

    token_resp = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": api_key},
        timeout=15,
    )
    token_resp.raise_for_status()
    token = token_resp.json()["access_token"]

    gen_resp = requests.post(
        f"{url}/ml/v1/text/generation?version=2023-05-29",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={
            "model_id": model,
            "input": prompt,
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": 2000,
                "stop_sequences": ["--- END ---"],
            },
            "project_id": project_id,
        },
        timeout=60,
    )
    gen_resp.raise_for_status()
    return gen_resp.json()["results"][0]["generated_text"]


def _demo_fallback(source_path: Path) -> str:
    """Return canned Bob-optimised COBOL from pre-built samples."""
    stem = source_path.stem
    samples = source_path.parent if "samples" in str(source_path) else Path(__file__).parent.parent / "emulator" / "samples"

    for suffix in ("_ai_safe", "_ai_clean"):
        candidate = samples / f"{stem}{suffix}.cob"
        if candidate.exists():
            return candidate.read_text(encoding="utf-8")

    text = source_path.read_text(encoding="utf-8")
    return re.sub(
        r"(PIC\s+9[^\n]+?)(\s*\.\s*$)",
        r"\1 COMP-3\2",
        text,
        flags=re.MULTILINE | re.IGNORECASE,
    )


def optimize(source_path: Path, output_path: Path | None = None) -> tuple[Path, str]:
    """
    Ask IBM Bob (Granite) to optimise a COBOL program.

    Returns (output_path, mode) where mode is 'granite' or 'demo'.
    """
    source_path = Path(source_path)
    source = source_path.read_text(encoding="utf-8")

    if output_path is None:
        output_path = source_path.parent / f"{source_path.stem}_bob_edit{source_path.suffix}"

    mode = "granite"
    try:
        rag_context = _get_rag_context(source_path.stem, source)
        prompt = _build_optimize_prompt(source, rag_context)
        result = _call_granite(prompt)
        result = re.sub(r"^```[a-z]*\n?|```$", "", result.strip(), flags=re.MULTILINE).strip()
        print(f"  [Bob] IBM Granite rewrote {source_path.name} ({len(result)} chars)")
    except (KeyError, Exception) as exc:
        mode = "demo"
        print(f"  [Bob] Granite unavailable ({exc.__class__.__name__}), using pre-built optimised sample")
        result = _demo_fallback(source_path)

    Path(output_path).write_text(result, encoding="utf-8")
    return Path(output_path), mode
