from __future__ import annotations

import re
import tempfile
from pathlib import Path

from audit.equivalence import (
    _cobc_available,
    _has_file_section,
    _find_ws_numeric_inputs,
    _inject_test_values,
    _compile,
    _run_binary,
)
from audit.models import SemanticChange
from audit.pic_boundary import derive_boundaries

_ERROR_CLAUSES = [
    (r"\bON\s+SIZE\s+ERROR\b", "ON SIZE ERROR"),
    (r"\bINVALID\s+KEY\b",     "INVALID KEY"),
    (r"\bAT\s+END\b",          "AT END"),
    (r"\bON\s+OVERFLOW\b",     "ON OVERFLOW"),
]

def _check_static_clauses(orig_src: str, mod_src: str) -> list[SemanticChange]:
    changes: list[SemanticChange] = []
    for pattern, label in _ERROR_CLAUSES:
        orig_count = len(re.findall(pattern, orig_src, re.IGNORECASE))
        mod_count = len(re.findall(pattern, mod_src, re.IGNORECASE))
        if mod_count < orig_count:
            changes.append(SemanticChange(
                change_type="ERROR_HANDLER_REMOVED",
                location="PROCEDURE",
                original=f"{label} × {orig_count}",
                modified=f"{label} × {mod_count}",
                severity="HIGH",
            ))
    return changes


_ADVERSARIAL_CLASSES = [
    ("overflow",  lambda b: b.overflow_val),
    ("zero",      lambda b: "0"),
    ("near-max",  lambda b: b.max_val),
    ("negative",  lambda b: b.min_val),
]


def _run_adversarial(orig_src: str, mod_src: str) -> list[SemanticChange]:
    if _has_file_section(orig_src) or _has_file_section(mod_src):
        return []

    ws_fields = _find_ws_numeric_inputs(orig_src)
    if not ws_fields:
        return []

    boundaries = {name: derive_boundaries(pic, usage) for name, pic, usage in ws_fields}
    changes: list[SemanticChange] = []

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        for class_label, val_fn in _ADVERSARIAL_CLASSES:
            field_values = {name: val_fn(b) for name, b in boundaries.items()}
            orig_patched = _inject_test_values(orig_src, field_values)
            mod_patched = _inject_test_values(mod_src, field_values)

            label = class_label
            orig_src_path = tmp / f"orig_{label}.cob"
            mod_src_path = tmp / f"mod_{label}.cob"
            orig_bin = tmp / f"orig_bin_{label}"
            mod_bin = tmp / f"mod_bin_{label}"

            orig_src_path.write_text(orig_patched, encoding="utf-8")
            mod_src_path.write_text(mod_patched, encoding="utf-8")

            ok, _ = _compile(orig_src_path, orig_bin)
            if not ok:
                continue

            ok, _ = _compile(mod_src_path, mod_bin)
            if not ok:
                continue

            orig_out, _ = _run_binary(orig_bin)
            mod_out, _ = _run_binary(mod_bin)

            if orig_out != mod_out:
                changes.append(SemanticChange(
                    change_type="EXCEPTION_DIVERGENCE",
                    location=f"PROGRAM (round={class_label})",
                    original=orig_out[:300],
                    modified=mod_out[:300],
                    severity="HIGH",
                ))

    return changes


def check_exception_paths(
    original: Path,
    modified: Path,
    orig_src: str,
    mod_src: str,
) -> list[SemanticChange]:
    changes = _check_static_clauses(orig_src, mod_src)
    if _cobc_available():
        changes.extend(_run_adversarial(orig_src, mod_src))
    return changes
