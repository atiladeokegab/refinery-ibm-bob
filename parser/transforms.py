"""COBOL source transformations for Z-Optima RL (A0-A13).

apply_transform(action_id, source) -> str

Contract:
- Returns a new string; never mutates the input.
- Returns source unchanged when the target pattern is absent.
- Never raises — correctness is enforced at runtime by HERCULES.
"""

from __future__ import annotations

import re

# ── dispatch table ─────────────────────────────────────────────────────────────

def apply_transform(action_id: int, source: str) -> str:
    return _TRANSFORMS.get(action_id, _noop)(source)


# ── A0: COMPUTE_TO_ARITH ──────────────────────────────────────────────────────
# Replace simple single-operator COMPUTE with explicit ADD/SUBTRACT/MULTIPLY/DIVIDE.
# Complex expressions (multiple operators, parentheses) are left unchanged.

_COMPUTE_RE = re.compile(
    r"(COMPUTE\s+)(\S+)(\s*=\s*)(\S+)\s*([+\-*/])\s*(\S+)\s*\.",
    re.IGNORECASE,
)


def _compute_to_arith(source: str) -> str:
    def _replace(m: re.Match) -> str:
        dst, a, op, b = m.group(2), m.group(4), m.group(5), m.group(6)
        indent = re.match(r"^(\s*)", m.group(0)).group(1)
        if op == "+":
            return f"ADD {a} TO {b} GIVING {dst}."
        if op == "-":
            return f"SUBTRACT {b} FROM {a} GIVING {dst}."
        if op == "*":
            return f"MULTIPLY {a} BY {b} GIVING {dst}."
        if op == "/":
            return f"DIVIDE {b} INTO {a} GIVING {dst}."
        return m.group(0)

    return _COMPUTE_RE.sub(_replace, source)


# ── A1: STRING_TO_MOVE ────────────────────────────────────────────────────────
# Replace STRING X DELIMITED SIZE INTO Y (single source only) with MOVE X TO Y.

_STRING_SIMPLE_RE = re.compile(
    r"STRING\s+(\S+)\s+DELIMITED\s+SIZE\s+INTO\s+(\S+)\s*\.",
    re.IGNORECASE,
)


def _string_to_move(source: str) -> str:
    return _STRING_SIMPLE_RE.sub(lambda m: f"MOVE {m.group(1)} TO {m.group(2)}.", source)


# ── A2: ELIM_REDUNDANT_COMPUTE ────────────────────────────────────────────────
# Remove the first of two consecutive COMPUTEs to the same target variable.

_COMPUTE_LINE_RE = re.compile(
    r"^(\s*)(COMPUTE\s+(\S+)\s*=\s*[^\n]+\.)[ \t]*$",
    re.IGNORECASE | re.MULTILINE,
)


def _elim_redundant_compute(source: str) -> str:
    lines = source.splitlines(keepends=True)
    result: list[str] = []
    i = 0
    while i < len(lines):
        m1 = _COMPUTE_LINE_RE.match(lines[i].rstrip("\n"))
        if m1 and i + 1 < len(lines):
            m2 = _COMPUTE_LINE_RE.match(lines[i + 1].rstrip("\n"))
            if m2 and m1.group(3).upper() == m2.group(3).upper():
                i += 1  # skip the first (redundant) assignment
                continue
        result.append(lines[i])
        i += 1
    return "".join(result)


# ── A3: UNROLL_PERFORM ────────────────────────────────────────────────────────
# Expand PERFORM PARA N TIMES (N ≤ 4) into N sequential PERFORM PARA. statements.

_PERFORM_N_RE = re.compile(
    r"(\s*)(PERFORM\s+(\S+)\s+([1-4])\s+TIMES\s*\.)",
    re.IGNORECASE,
)


def _unroll_perform(source: str) -> str:
    def _expand(m: re.Match) -> str:
        indent, para, n = m.group(1), m.group(3), int(m.group(4))
        return "".join(f"{indent}PERFORM {para}.\n" for _ in range(n)).rstrip("\n")

    return _PERFORM_N_RE.sub(_expand, source)


# ── A4: HOIST_PERFORM_INVARIANT ───────────────────────────────────────────────
# Move MOVE literal TO var statements (loop-invariant) before a PERFORM...END-PERFORM.
# Conservative: only hoists if the moved-to variable is not the VARYING counter.

_PERFORM_VARYING_BLOCK_RE = re.compile(
    r"([ \t]*PERFORM\s+VARYING\s+(\S+)[^\n]*\n)"  # header line, group 2 = counter var
    r"((?:(?!END-PERFORM)[\s\S])*?)"               # body, group 3
    r"([ \t]*END-PERFORM\.?)",                      # closer, group 4
    re.IGNORECASE,
)

_MOVE_LITERAL_RE = re.compile(
    r"[ \t]*(MOVE\s+(?:'[^']*'|\d[\d.,]*)?\s+TO\s+(\S+)\s*\.)\n",
    re.IGNORECASE,
)


def _hoist_perform_invariant(source: str) -> str:
    def _hoist(m: re.Match) -> str:
        header   = m.group(1)
        counter  = m.group(2).upper()
        body     = m.group(3)
        closer   = m.group(4)

        hoisted: list[str] = []
        remaining_lines: list[str] = []

        for line in body.splitlines(keepends=True):
            lm = _MOVE_LITERAL_RE.match(line)
            if lm and lm.group(2).upper() != counter:
                hoisted.append(line)
            else:
                remaining_lines.append(line)

        if not hoisted:
            return m.group(0)

        return "".join(hoisted) + header + "".join(remaining_lines) + closer

    return _PERFORM_VARYING_BLOCK_RE.sub(_hoist, source)


# ── A5: UNTIL_TO_INLINE ───────────────────────────────────────────────────────
# Convert a simple PERFORM UNTIL counter >= literal block to an inline loop using
# an IF / GO TO structure. Only handles the simplest single-counter pattern.

_PERFORM_UNTIL_BLOCK_RE = re.compile(
    r"([ \t]*MOVE\s+0\s+TO\s+(\S+)\s*\.\n)"
    r"([ \t]*PERFORM\s+UNTIL\s+\2\s*>=\s*(\d+)\n)"
    r"((?:(?!END-PERFORM)[\s\S])*?)"
    r"([ \t]*END-PERFORM\.?)",
    re.IGNORECASE,
)


def _until_to_inline(source: str) -> str:
    def _inline(m: re.Match) -> str:
        init_line = m.group(1)
        counter   = m.group(2)
        limit     = m.group(4)
        body      = m.group(5)
        indent    = re.match(r"^(\s*)", m.group(3)).group(1)
        label     = f"LOOP-{counter[:4].replace('-', '')}"

        return (
            init_line
            + f"{indent}{label}.\n"
            + body
            + f"{indent}    ADD 1 TO {counter}.\n"
            + f"{indent}    IF {counter} < {limit} GO TO {label}.\n"
        )

    return _PERFORM_UNTIL_BLOCK_RE.sub(_inline, source)


# ── A6: INCREASE_READ_BUFFER ──────────────────────────────────────────────────
# Inject BLOCK CONTAINS 10 RECORDS into FD entries that don't already have it.

_FD_RE = re.compile(
    r"([ \t]*FD\s+\S+\s*\.\n)(?![ \t]*BLOCK)",
    re.IGNORECASE,
)


def _increase_read_buffer(source: str) -> str:
    return _FD_RE.sub(
        lambda m: m.group(0).rstrip("\n") + "\n           BLOCK CONTAINS 10 RECORDS.\n",
        source,
    )


# ── A7: SEARCH_TO_BINARY ──────────────────────────────────────────────────────
# Replace SEARCH with SEARCH ALL.  Remove the preceding SET idx TO 1 (required
# for linear SEARCH, redundant/wrong for SEARCH ALL which sets its own index).

_SET_IDX_RE  = re.compile(r"[ \t]*SET\s+\S+-IDX\s+TO\s+1\s*\.\n", re.IGNORECASE)
_SEARCH_RE   = re.compile(r"\bSEARCH\b(?!\s+ALL)", re.IGNORECASE)


def _search_to_binary(source: str) -> str:
    source = _SET_IDX_RE.sub("", source)
    return _SEARCH_RE.sub("SEARCH ALL", source)


# ── A8: ELIM_DEAD_STORAGE ─────────────────────────────────────────────────────
# Remove top-level WORKING-STORAGE items (01/77) whose names never appear in
# the PROCEDURE DIVISION.

_WS_TOP_RE = re.compile(
    r"^[ \t]*(01|77)\s+([A-Z0-9][A-Z0-9-]*)(?:\s+REDEFINES\s+\S+)?\s+(?:PIC|PICTURE|VALUE)[^\n]*\.\n",
    re.IGNORECASE | re.MULTILINE,
)

_PROC_DIV_RE = re.compile(r"PROCEDURE\s+DIVISION", re.IGNORECASE)


def _elim_dead_storage(source: str) -> str:
    m = _PROC_DIV_RE.search(source)
    if not m:
        return source

    proc_text = source[m.start():].upper()

    def _is_used(name: str) -> bool:
        return name.upper() in proc_text

    def _maybe_remove(item: re.Match) -> str:
        name = item.group(2)
        if not _is_used(name):
            return ""
        return item.group(0)

    return _WS_TOP_RE.sub(_maybe_remove, source)


# ── A9: COMPRESS_REDEFINES ────────────────────────────────────────────────────
# Remove simple REDEFINES clauses where base and alias have identical PIC strings.

_REDEFINES_RE = re.compile(
    r"^([ \t]*01\s+\S+)\s+REDEFINES\s+(\S+)([ \t]+PIC\s+\S+[^\n]*)\.\n",
    re.IGNORECASE | re.MULTILINE,
)

_BASE_PIC_RE = re.compile(
    r"01\s+{base}\s+(PIC\s+\S+)",
    re.IGNORECASE,
)


def _compress_redefines(source: str) -> str:
    def _maybe_drop(m: re.Match) -> str:
        base = m.group(2)
        alias_pic = m.group(3).strip().upper()
        # [^\.\n]+ stops before the period so the comparison excludes it
        pat = re.compile(rf"01\s+{re.escape(base)}\s+(PIC\s+[^\.\n]+)", re.IGNORECASE)
        bm = pat.search(source)
        if bm and bm.group(1).upper().strip() == alias_pic:
            return ""   # identical PIC — drop the REDEFINES alias
        return m.group(0)

    return _REDEFINES_RE.sub(_maybe_drop, source)


# ── A10: COLLAPSE_88_CHAIN ────────────────────────────────────────────────────
# Replace multi-condition IF (var = A OR var = B OR ...) with the corresponding
# 88-level condition name when one is already declared in WORKING-STORAGE.

_88_DECL_RE = re.compile(
    r"88\s+([A-Z0-9][A-Z0-9-]*)\s+VALUES?\s+((?:'[^']*'|\"[^\"]*\")(?:\s*,\s*(?:'[^']*'|\"[^\"]*\"))*)\s*\.",
    re.IGNORECASE,
)

_MULTI_COND_RE = re.compile(
    r"IF\s+(\S+)\s*=\s*('[^']+')\s+OR\s+\1\s*=\s*('[^']+')\s*",
    re.IGNORECASE,
)


def _collapse_88_chain(source: str) -> str:
    # Build map of {frozenset(values): condition_name}
    cond_map: dict[frozenset, str] = {}
    for m in _88_DECL_RE.finditer(source):
        name = m.group(1)
        vals = frozenset(v.strip().strip("'\"").upper() for v in m.group(2).split(","))
        cond_map[vals] = name

    def _replace_if(m: re.Match) -> str:
        v1 = m.group(2).strip("'").upper()
        v2 = m.group(3).strip("'").upper()
        key = frozenset([v1, v2])
        if key in cond_map:
            return f"IF {cond_map[key]} "
        return m.group(0)

    return _MULTI_COND_RE.sub(_replace_if, source)


# ── A11: MERGE_SEQ_READS ─────────────────────────────────────────────────────
# Merge two consecutive READ FILE INTO WS-A / READ FILE INTO WS-B into one READ
# followed by a MOVE.

_TWO_READS_RE = re.compile(
    r"([ \t]*READ\s+(\S+)\s+INTO\s+(\S+)\s*\n"
    r"(?:[ \t]*AT\s+END[^\n]*\n)?"
    r"(?:[ \t]*END-READ\s*\.?\n)?)"
    r"([ \t]*READ\s+\2\s+INTO\s+(\S+)\s*\n"
    r"(?:[ \t]*AT\s+END[^\n]*\n)?"
    r"(?:[ \t]*END-READ\s*\.?\n)?)",
    re.IGNORECASE,
)


def _merge_seq_reads(source: str) -> str:
    def _merge(m: re.Match) -> str:
        file_  = m.group(2)
        first_ = m.group(3)
        second = m.group(5)
        indent = re.match(r"^(\s*)", m.group(1)).group(1)
        return (
            f"{indent}READ {file_} INTO {first_}\n"
            f"{indent}    AT END MOVE 'Y' TO WS-EOF-FLAG\n"
            f"{indent}END-READ.\n"
            f"{indent}MOVE {first_} TO {second}.\n"
        )

    return _TWO_READS_RE.sub(_merge, source)


# ── A12: PARALLEL_SORT_HINT ───────────────────────────────────────────────────
# Prepend a ZOPTIMA comment before each SORT statement to mark it for
# JCL-level parallelism hints downstream.

_SORT_STMT_RE = re.compile(r"^([ \t]*)(SORT\s+\S+)", re.IGNORECASE | re.MULTILINE)


def _parallel_sort_hint(source: str) -> str:
    return _SORT_STMT_RE.sub(r"\1* ZOPTIMA-PARALLEL-SORT\n\1\2", source)


# ── A13: NOOP ─────────────────────────────────────────────────────────────────

def _noop(source: str) -> str:
    return source


# ── dispatch table ─────────────────────────────────────────────────────────────

_TRANSFORMS: dict[int, callable] = {
    0:  _compute_to_arith,
    1:  _string_to_move,
    2:  _elim_redundant_compute,
    3:  _unroll_perform,
    4:  _hoist_perform_invariant,
    5:  _until_to_inline,
    6:  _increase_read_buffer,
    7:  _search_to_binary,
    8:  _elim_dead_storage,
    9:  _compress_redefines,
    10: _collapse_88_chain,
    11: _merge_seq_reads,
    12: _parallel_sort_hint,
    13: _noop,
}
