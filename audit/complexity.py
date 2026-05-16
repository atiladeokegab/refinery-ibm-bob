from __future__ import annotations

import re

# Each pattern counts one decision point.
# Negative lookbehind (?<!-) excludes END-IF, END-EVALUATE, etc.
_DECISION_PATTERNS = [
    r"(?<!-)\bIF\b",
    r"(?<!-)\bEVALUATE\b",
    r"\bWHEN\b",
    r"\bUNTIL\b",
    r"\bAT END\b",
    r"\bON EXCEPTION\b",
    r"\bON OVERFLOW\b",
    r"\bINVALID KEY\b",
]

_PROC_RE = re.compile(
    r"PROCEDURE\s+DIVISION\b(.*)",
    re.IGNORECASE | re.DOTALL,
)


def cyclomatic_complexity(source: str) -> int:
    proc_match = _PROC_RE.search(source)
    proc_text = proc_match.group(1) if proc_match else source
    count = sum(
        len(re.findall(pattern, proc_text, re.IGNORECASE))
        for pattern in _DECISION_PATTERNS
    )
    return 1 + count
