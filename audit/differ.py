from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from audit.ast_diff import check_computes_ast, check_data_types_ast, check_verb_counts_ast
from audit.complexity import cyclomatic_complexity
from audit.cfg import build_call_graph, diff_call_graphs
from audit.equivalence import check_equivalence
from audit.exception_injection import check_exception_paths
from audit.io_tracer import check_io_sequence
from audit.redefines import check_redefines
from audit.models import SemanticChange  # noqa: F401 — re-exported for callers
from emulator.synthetic_runner import SyntheticRunner
from parser.cobol_parser import COBOLParser

_mvs_path = os.environ.get("HERCULES_MVS_PATH")
if _mvs_path:
    from emulator.real_runner import RealHerculesRunner
    _runner = RealHerculesRunner.from_mvs_path(_mvs_path)
    _runner_type = "RealHerculesRunner"
else:
    _runner = SyntheticRunner()
    _runner_type = "SyntheticRunner"

_parser = COBOLParser()


@dataclass
class DiffResult:
    program_original: str
    program_modified: str
    cpu_before_us: int
    cpu_after_us: int
    reduction_pct: float
    semantic_changes: list[SemanticChange]
    verdict: Literal["PASS", "FLAGGED"]
    risk_score: int = 0
    features_original: dict = field(default_factory=dict)
    features_modified: dict = field(default_factory=dict)
    equivalence_result: str = "SKIPPED"
    equivalence_detail: str = ""
    runner_type: str = "SyntheticRunner"
    checks_run: int = 6
    cyclomatic_complexity_original: int = 0
    cyclomatic_complexity_modified: int = 0


def _us(elapsed_cycles: float) -> int:
    return int(elapsed_cycles * 1_000_000)


def _extract_computes(source: str) -> list[str]:
    """Return normalised COMPUTE statement strings (multi-line collapsed)."""
    raw = re.findall(r"COMPUTE\b[^\n]+(?:\n[ \t]+[^\n]+)*", source, re.IGNORECASE)
    return [re.sub(r"\s+", " ", m).strip() for m in raw]


def _find_paragraph(source: str, match_start: int) -> str:
    """Return the paragraph name immediately above match_start."""
    before = source[:match_start]
    hits = list(re.finditer(r"^\s{4,11}([A-Z0-9][\w-]+)\.$", before, re.MULTILINE | re.IGNORECASE))
    return hits[-1].group(1) if hits else "PROCEDURE"


def _check_computes(orig_src: str, mod_src: str) -> list[SemanticChange]:
    orig = _extract_computes(orig_src)
    mod = _extract_computes(mod_src)
    changes: list[SemanticChange] = []

    orig_matches = list(re.finditer(r"COMPUTE\b", orig_src, re.IGNORECASE))
    for i, (o, m) in enumerate(zip(orig, mod)):
        if o != m:
            loc = _find_paragraph(orig_src, orig_matches[i].start()) if i < len(orig_matches) else "PROCEDURE"
            changes.append(SemanticChange(
                change_type="COMPUTE_EXPR",
                location=loc,
                original=o,
                modified=m,
                severity="HIGH",
            ))

    if len(orig) != len(mod):
        changes.append(SemanticChange(
            change_type="COMPUTE_EXPR",
            location="PROCEDURE",
            original=f"{len(orig)} COMPUTE verbs",
            modified=f"{len(mod)} COMPUTE verbs",
            severity="HIGH",
        ))
    return changes


def _extract_pic_fields(source: str) -> dict[str, dict]:
    """Return {field_name: {pic, comp3}} for all PIC-declared fields."""
    result: dict[str, dict] = {}
    for m in re.finditer(
        r"\b(\d{2})\s+([\w-]+)\s+PIC(?:TURE)?\s+(?:IS\s+)?([S9XAV()\/\d]+)((?:\s+COMP-3)?)",
        source,
        re.IGNORECASE,
    ):
        name = m.group(2)
        pic = re.sub(r"\s+", "", m.group(3)).upper()
        comp3 = bool(m.group(4).strip())
        result[name] = {"pic": pic, "comp3": comp3}
    return result


def _check_data_types(orig_src: str, mod_src: str) -> list[SemanticChange]:
    orig_fields = _extract_pic_fields(orig_src)
    mod_fields = _extract_pic_fields(mod_src)
    changes: list[SemanticChange] = []

    for name, orig_info in orig_fields.items():
        if name not in mod_fields:
            continue
        mod_info = mod_fields[name]
        if orig_info["pic"] != mod_info["pic"]:
            changes.append(SemanticChange(
                change_type="DATA_TYPE",
                location=name,
                original=f"PIC {orig_info['pic']}",
                modified=f"PIC {mod_info['pic']}",
                severity="HIGH",
            ))
        elif orig_info["comp3"] != mod_info["comp3"]:
            orig_str = f"PIC {orig_info['pic']}" + (" COMP-3" if orig_info["comp3"] else "")
            mod_str = f"PIC {mod_info['pic']}" + (" COMP-3" if mod_info["comp3"] else "")
            changes.append(SemanticChange(
                change_type="DATA_TYPE",
                location=name,
                original=orig_str,
                modified=mod_str,
                severity="MEDIUM",  # storage-format change — affects VSAM layouts and downstream systems
            ))
    return changes


def _count_verb(source: str, verb: str) -> int:
    return len(re.findall(rf"\b{verb}\b", source, re.IGNORECASE))


def _check_verb_counts(orig_src: str, mod_src: str) -> list[SemanticChange]:
    changes: list[SemanticChange] = []
    for verb in ("PERFORM", "SEARCH", "SORT"):
        o = _count_verb(orig_src, verb)
        m = _count_verb(mod_src, verb)
        if o != m:
            changes.append(SemanticChange(
                change_type="VERB_COUNT",
                location="PROCEDURE",
                original=f"{verb}={o}",
                modified=f"{verb}={m}",
                severity="MEDIUM",
            ))
    return changes


def _verdict(changes: list[SemanticChange]) -> Literal["PASS", "FLAGGED"]:
    severities = {c.severity for c in changes}
    if "HIGH" in severities or "MEDIUM" in severities:
        return "FLAGGED"
    return "PASS"


_SEVERITY_WEIGHTS = {"HIGH": 40, "MEDIUM": 15, "LOW": 5}


def _risk_score(changes: list[SemanticChange]) -> int:
    return min(100, sum(_SEVERITY_WEIGHTS.get(c.severity, 0) for c in changes))


def run_diff(original: Path, modified: Path, repo_root: Path | None = None) -> DiffResult:
    orig_src = Path(original).read_text(encoding="utf-8")
    mod_src = Path(modified).read_text(encoding="utf-8")

    orig_tel = _runner.run(original)
    mod_tel = _runner.run(modified)

    cpu_before = _us(orig_tel["elapsed_cycles"])
    cpu_after = _us(mod_tel["elapsed_cycles"])

    features_orig = _parser.extract_features(orig_src)
    features_mod = _parser.extract_features(mod_src)

    changes: list[SemanticChange] = []

    # Use AST-based checks when tree-sitter grammar is available and both trees
    # parse cleanly; fall back to regex if either tree has parse errors.
    orig_tree = _parser.parse(orig_src)
    mod_tree  = _parser.parse(mod_src)

    _use_ast = (
        orig_tree is not None and mod_tree is not None
        and not orig_tree.root_node.has_error
        and not mod_tree.root_node.has_error
    )

    if _use_ast:
        changes.extend(check_computes_ast(orig_tree, mod_tree, orig_src, mod_src))
        data_changes = check_data_types_ast(orig_tree, mod_tree, orig_src, mod_src)
        changes.extend(data_changes)
        changes.extend(check_verb_counts_ast(orig_tree, mod_tree))
    else:
        # Fallback: tree-sitter grammar unavailable or parse errors detected
        changes.extend(_check_computes(orig_src, mod_src))
        data_changes = _check_data_types(orig_src, mod_src)
        changes.extend(data_changes)
        changes.extend(_check_verb_counts(orig_src, mod_src))

    changes.extend(check_redefines(orig_src, mod_src))

    # Layer 2: procedure call graph
    orig_graph = build_call_graph(orig_src)
    mod_graph  = build_call_graph(mod_src)
    changes.extend(diff_call_graphs(orig_graph, mod_graph))

    # Layer 3: GnuCOBOL output equivalence
    equiv = check_equivalence(original, modified, repo_root=repo_root)
    changes.extend(equiv.semantic_changes)

    # Layer 5: Exception path injection
    changes.extend(check_exception_paths(original, modified, orig_src, mod_src))

    # Layer 6: I/O event sequence
    changes.extend(check_io_sequence(orig_src, mod_src))

    # COMP-3 (packed decimal) is ~6% faster per field on z/Architecture packed arithmetic.
    # SyntheticRunner doesn't model storage format, so we apply the benefit here.
    comp3_gains = sum(
        1 for c in data_changes
        if c.change_type == "DATA_TYPE" and "COMP-3" in c.modified and "COMP-3" not in c.original
    )
    if comp3_gains > 0 and cpu_after > 0:
        cpu_after = max(1, int(cpu_after * (1.0 - 0.06 * comp3_gains)))

    reduction = (cpu_before - cpu_after) / cpu_before * 100 if cpu_before > 0 else 0.0

    return DiffResult(
        program_original=Path(original).name,
        program_modified=Path(modified).name,
        cpu_before_us=cpu_before,
        cpu_after_us=cpu_after,
        reduction_pct=round(reduction, 1),
        semantic_changes=changes,
        verdict=_verdict(changes),
        risk_score=_risk_score(changes),
        features_original=features_orig,
        features_modified=features_mod,
        equivalence_result=equiv.status,
        equivalence_detail=equiv.detail,
        runner_type=_runner_type,
        checks_run=8,
        cyclomatic_complexity_original=cyclomatic_complexity(orig_src),
        cyclomatic_complexity_modified=cyclomatic_complexity(mod_src),
    )
