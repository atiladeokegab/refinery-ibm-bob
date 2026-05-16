from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from audit.engine import AuditResult, run_audit as _run_audit
from audit.models import SemanticChange
from bob.optimizer import _call_granite

_CORRECTION_PROMPT = """\
SPECIFIC FAILURE: {change_type} at {location}
  You changed "{original}" to "{modified}". This alters business logic.

KNOWN RELATED PATTERNS:
{rag_patterns}
INSTRUCTION: Fix ONLY the issue above. Do not change anything else.
Return the complete corrected COBOL program with no explanation or markdown.

CURRENT COBOL (your edit):
{bob_edit_source}
"""


@dataclass
class CorrectionResult:
    final_path: Path
    final_audit: AuditResult
    correction_count: int
    succeeded: bool


def _get_correction_rag(change_type: str, location: str) -> str:
    try:
        # Lazy import: RAG failures must not break correction loop.
        from bob.rag.retriever import retrieve
        query = f"COBOL {change_type} {location} optimization mistake"
        chunks = retrieve(query, top_k=2)
        if not chunks:
            return "  (no known patterns for this failure type)\n"
        return "\n".join(f"  - {c.text[:300]}" for c in chunks) + "\n"
    except Exception:
        return "  (patterns unavailable)\n"


def _primary_failure(changes: list[SemanticChange]) -> SemanticChange | None:
    high = [c for c in changes if c.severity == "HIGH"]
    med = [c for c in changes if c.severity == "MEDIUM"]
    candidates = high or med or changes
    return candidates[0] if candidates else None


def correct(
    original_path: Path,
    modified_path: Path,
    initial_audit: AuditResult,
    max_retries: int = 2,
) -> CorrectionResult:
    """
    Given a FLAGGED initial audit, ask Bob to self-correct (max_retries times).
    Returns the best result achieved and how many correction rounds were used.
    """
    current_path = Path(modified_path)
    current_audit = initial_audit
    correction_count = 0

    for _ in range(max_retries):
        primary = _primary_failure(current_audit.diff.semantic_changes)
        if primary is None:
            break

        bob_edit_source = current_path.read_text(encoding="utf-8")
        rag_patterns = _get_correction_rag(primary.change_type, primary.location)
        prompt = _CORRECTION_PROMPT.format(
            change_type=primary.change_type,
            location=primary.location,
            original=primary.original,
            modified=primary.modified,
            rag_patterns=rag_patterns,
            bob_edit_source=bob_edit_source,
        )

        try:
            corrected_src = _call_granite(prompt)
            corrected_src = re.sub(
                r"^```[a-z]*\n?|```$", "", corrected_src.strip(), flags=re.MULTILINE
            ).strip()
        except Exception:
            break

        current_path.write_text(corrected_src, encoding="utf-8")
        correction_count += 1
        current_audit = _run_audit(original_path, current_path)

        if current_audit.diff.verdict == "PASS":
            break

    return CorrectionResult(
        final_path=current_path,
        final_audit=current_audit,
        correction_count=correction_count,
        succeeded=current_audit.diff.verdict == "PASS",
    )
