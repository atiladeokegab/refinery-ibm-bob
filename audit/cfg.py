from __future__ import annotations
import re
from dataclasses import dataclass, field
from audit.models import SemanticChange


@dataclass
class CallGraph:
    paragraphs: list[str] = field(default_factory=list)
    edges: dict[str, list[str]] = field(default_factory=dict)
    # (target, is_conditional) per occurrence — True if PERFORM is inside IF/EVALUATE
    conditional_edges: dict[str, list[tuple[str, bool]]] = field(default_factory=dict)


_PARA_RE = re.compile(
    r"^\s{4,11}([A-Z0-9][\w-]+)\.\s*$", re.MULTILINE | re.IGNORECASE
)
_PERFORM_RE = re.compile(
    r"\bPERFORM\s+(?!UNTIL\b|THRU\b|THROUGH\b|VARYING\b|WITH\b|TEST\b|TIMES\b)([A-Z0-9][\w-]+)",
    re.IGNORECASE,
)
_COMMENT_RE = re.compile(r"^\s{0,5}\*[^\n]*", re.MULTILINE)

# Mask END-IF/END-EVALUATE first so their IF/EVALUATE suffix doesn't trigger open detection
_END_MASK_RE  = re.compile(r"\bEND-(IF|EVALUATE)\b", re.IGNORECASE)
_COND_OPEN_RE = re.compile(r"\b(IF|EVALUATE)\b", re.IGNORECASE)
_COND_CLOSE_RE = re.compile(r"\bEND-(IF|EVALUATE)\b", re.IGNORECASE)

_RESERVED_WORDS = frozenset({
    "CONTINUE", "STOP", "MOVE", "ADD", "SUBTRACT", "MULTIPLY", "DIVIDE",
    "COMPUTE", "EVALUATE", "IF", "ELSE", "END-IF", "END-EVALUATE",
    "END-PERFORM", "END-COMPUTE", "INITIALIZE", "INSPECT", "STRING",
    "UNSTRING", "ACCEPT", "DISPLAY", "OPEN", "CLOSE", "READ", "WRITE",
    "REWRITE", "DELETE", "START", "RETURN", "CALL", "CANCEL", "GOBACK",
    "EXIT", "NEXT", "SENTENCE", "GO", "SECTION", "DIVISION",
})


def _find_conditional_performs(body: str) -> list[tuple[str, bool]]:
    """Return (target, is_conditional) for each PERFORM in body.

    is_conditional=True means the PERFORM is nested inside an IF or EVALUATE block.
    Requires structured delimiters (END-IF / END-EVALUATE); period-terminated IFs
    are not tracked.
    """
    stripped = _COMMENT_RE.sub("", body)
    # Replace END-IF/END-EVALUATE with spaces so _COND_OPEN_RE doesn't fire on
    # the IF/EVALUATE suffix inside them — positions stay identical.
    masked = _END_MASK_RE.sub(lambda m: " " * len(m.group()), stripped)

    events: list[tuple[int, object]] = []
    for m in _COND_CLOSE_RE.finditer(stripped):
        events.append((m.start(), "close"))
    for m in _COND_OPEN_RE.finditer(masked):
        events.append((m.start(), "open"))
    for m in _PERFORM_RE.finditer(stripped):
        target = m.group(1).upper()
        if target not in _RESERVED_WORDS:
            events.append((m.start(), ("perform", target)))

    events.sort(key=lambda e: e[0])

    result: list[tuple[str, bool]] = []
    depth = 0
    for _, kind in events:
        if kind == "open":
            depth += 1
        elif kind == "close":
            depth = max(0, depth - 1)
        else:
            _, target = kind
            result.append((target, depth > 0))

    return result


def build_call_graph(source: str) -> CallGraph:
    all_matches = list(_PARA_RE.finditer(source))
    para_matches = [m for m in all_matches if m.group(1).upper() not in _RESERVED_WORDS]
    graph = CallGraph()
    for i, m in enumerate(para_matches):
        name = m.group(1).upper()
        graph.paragraphs.append(name)
        start = m.end()
        end = para_matches[i + 1].start() if i + 1 < len(para_matches) else len(source)
        body = source[start:end]
        stripped_body = _COMMENT_RE.sub("", body)
        graph.edges[name] = [p.upper() for p in _PERFORM_RE.findall(stripped_body)]
        graph.conditional_edges[name] = _find_conditional_performs(body)
    return graph


def diff_call_graphs(orig: CallGraph, mod: CallGraph) -> list[SemanticChange]:
    changes: list[SemanticChange] = []
    orig_set = set(orig.paragraphs)
    mod_set  = set(mod.paragraphs)

    for p in orig_set - mod_set:
        changes.append(SemanticChange(
            change_type="CFG_REMOVED_PARAGRAPH",
            location=p, original=p, modified="(removed)", severity="HIGH",
        ))

    for p in mod_set - orig_set:
        changes.append(SemanticChange(
            change_type="CFG_ADDED_PARAGRAPH",
            location=p, original="(new)", modified=p, severity="MEDIUM",
        ))

    for p in orig_set & mod_set:
        orig_calls = orig.edges.get(p, [])
        mod_calls  = mod.edges.get(p, [])
        if orig_calls != mod_calls:
            if sorted(orig_calls) == sorted(mod_calls):
                changes.append(SemanticChange(
                    change_type="CFG_REORDERED_CALLS",
                    location=p,
                    original=" -> ".join(orig_calls),
                    modified=" -> ".join(mod_calls),
                    severity="HIGH",
                ))
            else:
                for target in set(orig_calls) - set(mod_calls):
                    changes.append(SemanticChange(
                        change_type="CFG_DROPPED_EDGE",
                        location=p,
                        original=f"PERFORM {target}",
                        modified="(removed)",
                        severity="HIGH",
                    ))
                for target in set(mod_calls) - set(orig_calls):
                    changes.append(SemanticChange(
                        change_type="CFG_ADDED_EDGE",
                        location=p,
                        original="(new)",
                        modified=f"PERFORM {target}",
                        severity="MEDIUM",
                    ))

        # Conditionality check — edges present in both versions
        orig_ce = orig.conditional_edges.get(p, [])
        mod_ce  = mod.conditional_edges.get(p, [])
        shared_targets = {t for t, _ in orig_ce} & {t for t, _ in mod_ce}

        for target in shared_targets:
            orig_has_uncond = any(not cond for t, cond in orig_ce if t == target)
            mod_has_uncond  = any(not cond for t, cond in mod_ce  if t == target)

            if orig_has_uncond and not mod_has_uncond:
                changes.append(SemanticChange(
                    change_type="CFG_CONDITIONALITY_CHANGED",
                    location=p,
                    original=f"PERFORM {target} (unconditional)",
                    modified=f"PERFORM {target} (wrapped in IF/EVALUATE)",
                    severity="HIGH",
                ))
            elif not orig_has_uncond and mod_has_uncond:
                changes.append(SemanticChange(
                    change_type="CFG_CONDITIONALITY_CHANGED",
                    location=p,
                    original=f"PERFORM {target} (conditional)",
                    modified=f"PERFORM {target} (unconditional)",
                    severity="HIGH",
                ))

    return changes
