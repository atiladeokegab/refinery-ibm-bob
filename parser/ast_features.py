"""AST and regex-based feature extraction for COBOL source programs."""

import re

_BLANK_RE = re.compile(r"^\s*$")


def _code_lines(source: str) -> list[str]:
    """Non-blank, non-comment lines (fixed-format column-7 aware)."""
    out = []
    for line in source.splitlines():
        if _BLANK_RE.match(line):
            continue
        # Fixed-format COBOL: column 7 (index 6) is '*' or '/' for comments
        if len(line) > 6 and line[6] in ("*", "/"):
            continue
        out.append(line)
    return out


def _perform_depth(source: str) -> int:
    """Max PERFORM nesting depth by bracket-matching PERFORM / END-PERFORM."""
    depth = 0
    max_depth = 0
    for m in re.finditer(r"\bEND-PERFORM\b|\bPERFORM\b", source, re.IGNORECASE):
        if m.group().upper() == "PERFORM":
            depth += 1
            max_depth = max(max_depth, depth)
        else:
            depth = max(0, depth - 1)
    return max_depth


def _pic_bytes(pic: str) -> int:
    """Rough byte estimate for a single PICTURE clause string."""
    expanded = re.sub(
        r"([X9A])\((\d+)\)",
        lambda m: m.group(1) * int(m.group(2)),
        pic.upper(),
    )
    return max(len(re.findall(r"[X9A]", expanded)), 1)


def _working_storage_bytes(source: str) -> int:
    """Estimate WORKING-STORAGE size by summing PIC clause byte widths."""
    ws_match = re.search(
        r"WORKING-STORAGE\s+SECTION\s*\.(.*?)"
        r"(?=\b(?:FILE|LINKAGE|LOCAL-STORAGE|COMMUNICATION|REPORT|SCREEN)\s+SECTION\b|\Z)",
        source,
        re.IGNORECASE | re.DOTALL,
    )
    if not ws_match:
        return 0
    ws_text = ws_match.group(1)
    total = sum(
        _pic_bytes(m.group(1))
        for m in re.finditer(
            r"\bPIC(?:TURE)?\b\s+(?:IS\s+)?([S9XAV()\d]+)",
            ws_text,
            re.IGNORECASE,
        )
    )
    return max(total, 0)


def _file_section_count(source: str) -> int:
    return len(re.findall(r"\bFILE\s+SECTION\b", source, re.IGNORECASE))


def _verb_count(source: str, verb: str) -> int:
    return len(re.findall(rf"\b{verb}\b", source, re.IGNORECASE))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_from_regex(source: str) -> dict:
    """Return COBOLState AST fields using pure regex analysis."""
    lines = _code_lines(source)
    return {
        "loc": len(lines),
        "perform_depth": _perform_depth(source),
        "working_storage_bytes": _working_storage_bytes(source),
        "file_section_count": _file_section_count(source),
        "compute_verb_count": _verb_count(source, "COMPUTE"),
        "search_verb_count": _verb_count(source, "SEARCH"),
        "sort_verb_count": _verb_count(source, "SORT"),
    }


def extract_from_tree(tree, source: str) -> dict:
    """Walk a tree-sitter AST; fall back to regex for unrecognised node types."""
    features = extract_from_regex(source)

    ast_counts: dict[str, int] = {
        "compute_verb_count": 0,
        "search_verb_count": 0,
        "sort_verb_count": 0,
    }
    _VERB_KEYS = {
        "compute": "compute_verb_count",
        "search": "search_verb_count",
        "sort": "sort_verb_count",
    }

    def walk(node) -> None:
        ntype = node.type.lower()
        for kw, key in _VERB_KEYS.items():
            if ntype == f"{kw}_statement":
                ast_counts[key] += 1
                break
        for child in node.children:
            walk(child)

    walk(tree.root_node)

    # Only override regex counts when the AST grammar actually recognised the nodes
    for key, count in ast_counts.items():
        if count > 0:
            features[key] = count

    return features
