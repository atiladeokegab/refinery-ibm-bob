from __future__ import annotations

import re
from dataclasses import dataclass

from audit.models import SemanticChange

# Match EXEC SQL <verb> [INTO|FROM] <table>
_EXEC_SQL_RE = re.compile(
    r"\bEXEC\s+SQL\s+(UPDATE|INSERT|DELETE|SELECT)\s+(?:(?:INTO|FROM)\s+)?([\w-]+)",
    re.IGNORECASE,
)
# Match COBOL file verbs — requires whitespace after verb to avoid matching hyphenated names
_FILE_VERB_RE = re.compile(
    r"\b(READ|WRITE|REWRITE|DELETE|OPEN|CLOSE)\s+([\w-]+)",
    re.IGNORECASE,
)


@dataclass
class IOEvent:
    verb: str
    target: str
    line_no: int


def extract_io_sequence(source: str) -> list[IOEvent]:
    pd_match = re.search(r"\bPROCEDURE\s+DIVISION\b", source, re.IGNORECASE)
    proc_src = source[pd_match.start():] if pd_match else source

    events: list[IOEvent] = []
    for i, line in enumerate(proc_src.splitlines(), 1):
        m = _EXEC_SQL_RE.search(line)
        if m:
            events.append(IOEvent(
                verb=f"EXEC SQL {m.group(1).upper()}",
                target=m.group(2).upper(),
                line_no=i,
            ))
            continue
        m = _FILE_VERB_RE.search(line)
        if m:
            events.append(IOEvent(
                verb=m.group(1).upper(),
                target=m.group(2).upper(),
                line_no=i,
            ))
    return events


def _fmt(seq: list[IOEvent]) -> str:
    if not seq:
        return "(none)"
    return " | ".join(f"{i + 1}. {e.verb} {e.target}" for i, e in enumerate(seq))


def check_io_sequence(orig_src: str, mod_src: str) -> list[SemanticChange]:
    orig_seq = extract_io_sequence(orig_src)
    mod_seq = extract_io_sequence(mod_src)

    if not orig_seq and not mod_seq:
        return []

    orig_events = [(e.verb, e.target) for e in orig_seq]
    mod_events = [(e.verb, e.target) for e in mod_seq]

    changes: list[SemanticChange] = []

    for verb, target in orig_events:
        if (verb, target) not in mod_events:
            changes.append(SemanticChange(
                change_type="IO_REMOVED",
                location=target,
                original=f"{verb} {target}",
                modified="(removed)",
                severity="HIGH",
            ))

    if orig_events != mod_events:
        changes.append(SemanticChange(
            change_type="IO_SEQUENCE",
            location="PROCEDURE",
            original=_fmt(orig_seq),
            modified=_fmt(mod_seq),
            severity="HIGH",
        ))

    return changes
