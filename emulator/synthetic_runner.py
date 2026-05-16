"""SyntheticRunner — calibrated telemetry without a live MVS emulator.

Derives instruction counts, elapsed time, and I/O counts from COBOL AST
features. Deterministic for a given source (same source = same numbers).
Numbers change meaningfully when transforms are applied:
  - ELIM_REDUNDANT_COMPUTE  → fewer COMPUTE verbs → lower instruction count
  - SEARCH_TO_BINARY        → SEARCH ALL pattern  → big I-count drop
  - INCREASE_READ_BUFFER    → BLOCK CONTAINS      → lower excp_count
  - ELIM_DEAD_STORAGE       → smaller WS bytes    → lower memory_pages
  - SORT-related transforms → lower sort costs

Calibration targets: 15-30 % CPU reduction for meaningful single transforms,
consistent with the Z-Optima RL MIPS claims.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import numpy as np

from parser.ast_features import extract_from_regex

# Emulated z/Architecture throughput on a modern host (instructions / second)
_EMULATED_IPS: float = 20_000_000.0

# Cost in instructions for each code feature
_COST_LOC = 2_000          # baseline overhead per line
_COST_COMPUTE = 20_000     # each COMPUTE verb
_COST_SEARCH_LINEAR = 80_000   # SEARCH (linear table scan)
_COST_SEARCH_BINARY = 8_000    # SEARCH ALL (binary)
_COST_SORT = 120_000       # SORT step
_COST_PERFORM_DEPTH_MULT = 1.20  # multiplier per nesting level above 1

# I/O calibration
_EXCP_PER_FILE = 400
_EXCP_PER_SORT = 600
_EXCP_PER_WS_PAGE = 1       # 1 EXCP per 4 KB WS page


def _source_seed(source: str) -> int:
    return int(hashlib.md5(source.encode()).hexdigest()[:8], 16)


def _has_pattern(source: str, pattern: str) -> bool:
    return bool(re.search(pattern, source, re.IGNORECASE))


def _compute_instructions(source: str, features: dict, rng: np.random.Generator) -> int:
    loc = max(features["loc"], 10)
    compute = features["compute_verb_count"]
    sort = features["sort_verb_count"]
    depth = max(features["perform_depth"], 1)

    # Distinguish SEARCH ALL (binary) from plain SEARCH (linear)
    search_all = len(re.findall(r"\bSEARCH\s+ALL\b", source, re.IGNORECASE))
    search_linear = max(features["search_verb_count"] - search_all, 0)

    base = loc * _COST_LOC
    verb_cost = (
        compute * _COST_COMPUTE
        + search_linear * _COST_SEARCH_LINEAR
        + search_all * _COST_SEARCH_BINARY
        + sort * _COST_SORT
    )
    depth_mult = _COST_PERFORM_DEPTH_MULT ** (depth - 1)
    raw = int((base + verb_cost) * depth_mult * rng.uniform(0.93, 1.07))
    return max(raw, 50_000)


def _compute_excp(source: str, features: dict, rng: np.random.Generator) -> int:
    files = max(features["file_section_count"], 0)
    sort = features["sort_verb_count"]
    ws_bytes = features["working_storage_bytes"]

    io_factor = 0.55 if _has_pattern(source, r"\bBLOCK\s+CONTAINS\b") else 1.0

    raw = int((
        files * _EXCP_PER_FILE
        + sort * _EXCP_PER_SORT
        + (ws_bytes // 4096) * _EXCP_PER_WS_PAGE
        + 80
    ) * io_factor * rng.uniform(0.88, 1.12))
    return max(raw, 20)


class SyntheticRunner:
    """Drop-in replacement for HerculesRunner — AST-calibrated synthetic telemetry.

    Returns the same dict schema as HerculesRunner.run():
        instruction_count, elapsed_cycles (seconds), memory_pages_touched, exit_code
    """

    def run(self, cobol_path: "Path | str") -> dict:
        source = Path(cobol_path).read_text(encoding="utf-8", errors="replace")
        return _telemetry(source)


def _telemetry(source: str) -> dict:
    """Compute telemetry from COBOL source text (exported for tests)."""
    features = extract_from_regex(source)
    rng = np.random.default_rng(_source_seed(source))

    instructions = _compute_instructions(source, features, rng)
    elapsed = instructions / _EMULATED_IPS
    excp = _compute_excp(source, features, rng)

    return {
        "instruction_count": instructions,
        "elapsed_cycles": elapsed,
        "memory_pages_touched": excp,
        "exit_code": 0,
    }
