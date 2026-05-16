from __future__ import annotations

import re
from datetime import date, datetime, timezone
from pathlib import Path

import bob.rag.retriever as _retriever
from audit.models import SemanticChange

_KB_DIR = Path(__file__).parent / "knowledge_base"


def ingest_failure(
    program: str,
    semantic_changes: list[SemanticChange],
    signal_type: str,
    reason: str | None = None,
) -> Path:
    """Write a failure record to the RAG knowledge base.

    signal_type: "semantic_failure" | "cro_rejection"
    Returns the path written (may not exist if nothing useful to write).
    """
    safe_program = re.sub(r"[^A-Za-z0-9._-]", "_", program)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = _KB_DIR / f"feedback_{timestamp}_{safe_program}.md"
    today = date.today().isoformat()

    body: list[str] = []

    if signal_type == "semantic_failure" and semantic_changes:
        high = [c for c in semantic_changes if c.severity == "HIGH"]
        med = [c for c in semantic_changes if c.severity == "MEDIUM"]
        notable = high or med or semantic_changes
        primary = notable[0]

        body += [
            f"# Known Bad Pattern: {primary.change_type} — {program}\n\n",
            f"**Signal:** Refinery FLAGGED  **Date:** {today}\n\n",
            "## What went wrong\n\n",
        ]
        for c in notable:
            body.append(
                f"At `{c.location}`: `{c.original}` was changed to `{c.modified}` "
                f"(severity: {c.severity}).\n\n"
            )
        body += [
            "## Pattern to avoid\n\n",
            f"Do NOT modify `{primary.location}` when optimising {program}-style programs. "
            f"The expression `{primary.original}` must be preserved exactly — "
            "changing it alters business logic.\n",
        ]

    elif signal_type == "cro_rejection" and reason:
        body += [
            f"# CRO Rejection: {program}\n\n",
            f"**Signal:** Human compliance decision  **Date:** {today}\n\n",
            "## Rejection reason\n\n",
            f"{reason}\n\n",
            "## Pattern to avoid\n\n",
            f"{reason}\n",
        ]

    if not body:
        return out_path  # nothing useful — caller checks .exists()

    out_path.write_text("".join(body), encoding="utf-8")
    _retriever._INDEX = None  # force rebuild on next retrieve()
    return out_path
