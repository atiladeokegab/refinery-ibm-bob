from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SemanticChange:
    change_type: str   # "COMPUTE_EXPR" | "DATA_TYPE" | "VERB_COUNT"
    location: str      # paragraph name or field name
    original: str
    modified: str
    severity: str      # "HIGH" | "MEDIUM" | "LOW"
